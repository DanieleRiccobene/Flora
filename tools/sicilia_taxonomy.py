"""FlorItaly 2023 -> species-level Sicily targets -> PlantCLEF inventory.

Reference: Gianni Bedini, Matteo Conti / floritaly; Checklist 27 April 2023.
Snapshot is versioned, not claimed to be a current or exhaustive 2026 checklist.
No fuzzy name matching. Subspecies/varieties are deliberately grouped at species level.
"""
import re
import hashlib
import unicodedata
from collections import defaultdict
import pandas as pd

REFERENCE_COMMIT = '6c4c7b08dc167a943907b2249b0a6b9684096f1d'
REFERENCE_URL = ('https://raw.githubusercontent.com/gibedini/floritaly/' + REFERENCE_COMMIT
                 + '/data-raw/CKL_27_04_2023.xlsx')
REFERENCE_SHA256 = '373c74e489b55868796151a8da1cc6a752c8bdb08ec6a0ed167a14ccec44feb8'
REFERENCE_DATE = '2023-04-27'


def species_name(value):
    """Conservative binomial parser; preserve named hybrids, reject formulas and qualifiers."""
    if value is None or pd.isna(value):
        return None
    text = ''.join(c for c in unicodedata.normalize('NFKD',str(value)) if not unicodedata.combining(c))
    text = re.sub(r'\s+', ' ', text.strip())
    if re.search(r'\?|\b(?:auct|sensu|cf|aff|non|nec)\b',text,re.I) or re.search(r'(?<!\w)p\.\s*p\.',text):
        return None
    if ' × ' in text and not re.match(r'^(?:×\s*)?[A-Z][a-z-]+ × [a-z-]+(?:\s|$)',text):
        return None
    match = re.match(r'^(×\s*)?([A-Z][a-z-]+)\s+(×\s*)?([a-z][a-z-]+)(?=\s|$)', text)
    if not match:
        return None
    genus_hybrid,genus,hybrid,epithet=match.groups()
    if epithet in {'sp','spp','sect','subsp','var','aggregate','agg'}:
        return None
    return ('×' if genus_hybrid else '') + genus + ' ' + ('×' if hybrid else '') + epithet


def norm(value):
    return (species_name(value) or '').casefold()


def build_reference(xlsx, include_casual=True, include_nonregional_names=False):
    ckl=pd.read_excel(xlsx,sheet_name='Checklist',keep_default_na=False)
    syn=pd.read_excel(xlsx,sheet_name='Sinonimi',keep_default_na=False)
    required={'Codice unico','entità','SIC'}
    if not required.issubset(ckl):
        raise ValueError('Schema checklist inatteso: verificare il formato.')
    ckl['canonical_species']=ckl['entità'].map(species_name)
    # (P) records at parent rank are grouped with their recorded subspecies.
    tokens=ckl.SIC.astype(str).str.replace(r'[()]',' ',regex=True).str.split()
    present=tokens.map(lambda t:'P' in t)
    if not include_casual:
        present &= ~tokens.map(lambda t:'CAS' in t)
    regional=ckl[present].copy()
    unparsed=regional[regional.canonical_species.isna()].copy()
    regional=regional.dropna(subset=['canonical_species'])
    targets=sorted(regional.canonical_species.unique())
    # Ambiguity is checked against the ENTIRE national checklist, including non-Sicilian taxa.
    destinations=defaultdict(set)
    accepted_by_id={str(row['Codice unico']):row['canonical_species']
                    for _,row in ckl.iterrows() if pd.notna(row['canonical_species'])}
    for name in ckl.canonical_species.dropna():
        destinations[norm(name)].add(name)
    for _,row in syn.iterrows():
        accepted=accepted_by_id.get(str(row['codice unico']))
        alias=str(row['sinonimo']).strip()
        # Known incorrect entry excluded by the source R package itself.
        if alias=='Sesleria apennina Ujhelyi':
            continue
        key=norm(alias)
        if accepted and key:
            destinations[key].add(accepted)
    target_set=set(targets)
    lookup={key:next(iter(values)) for key,values in destinations.items()
            if len(values)==1 and (include_nonregional_names or next(iter(values)) in target_set)}
    ambiguous=[{'normalized_name':key,'accepted_candidates':' | '.join(sorted(values))}
               for key,values in destinations.items() if len(values)>1 and (include_nonregional_names or values & target_set)]
    summary={'source_url':REFERENCE_URL,'snapshot_date':REFERENCE_DATE,
             'reference_sha256':REFERENCE_SHA256,'include_casual':include_casual,
             'selected_regional_taxa':int(present.sum()),'species_level_targets':len(targets),
             'unparsed_regional_taxa':len(unparsed),'ambiguous_names':len(ambiguous),
             'name_matching_scope':'national' if include_nonregional_names else 'regional',
             'scope':'vascular plants recorded as present in SIC; not all cultivated/ornamental species'}
    return targets,lookup,regional,unparsed,pd.DataFrame(ambiguous),summary


def audit_metadata(csv_path,targets,lookup,min_observations=20,chunksize=100000):
    """Exact counts of usable image IDs and independent observations, no image download."""
    observations=defaultdict(set)
    images=defaultdict(set)
    organ_counts=defaultdict(int)
    unmapped=defaultdict(int)
    invalid=defaultdict(int)
    inventory=defaultdict(int)
    per_class_source_names=defaultdict(set)
    columns=['species','obs_id','image_name','organ','image_backup_url','url']
    for chunk in pd.read_csv(csv_path,sep=';',usecols=columns,dtype=str,
                             keep_default_na=False,chunksize=chunksize):
        chunk=chunk.apply(lambda col:col.str.strip())
        for name,count in chunk.species.value_counts().items():
            inventory[name]+=int(count)
        mapped=chunk.species.map(norm).map(lookup)
        for name,count in chunk.loc[mapped.isna(),'species'].value_counts().items():
            unmapped[name]+=int(count)
        valid_url=chunk.image_backup_url.str.match(r'^https?://') | chunk.url.str.match(r'^https?://')
        valid=(chunk.obs_id!='') & (chunk.image_name!='') & valid_url
        for name,count in mapped[~valid].dropna().value_counts().items():
            invalid[name]+=int(count)
        chunk['canonical']=mapped
        for species,part in chunk[valid & mapped.notna()].groupby('canonical'):
            observations[species].update(part.obs_id)
            images[species].update(part.image_name)
            per_class_source_names[species].update(part.species)
            for organ,count in part.organ.str.casefold().replace('','unknown').value_counts().items():
                organ_counts[(species,organ)]+=int(count)
    records=[]
    for species in targets:
        obs_count=len(observations[species])
        status=('trainable' if obs_count>=min_observations else 'insufficient_observations'
                if obs_count else 'no_usable_match')
        records.append({'species':species,'observations':obs_count,'images':len(images[species]),
                        'invalid_rows':invalid[species],'status':status,
                        'plantclef_names':' | '.join(sorted(per_class_source_names[species]))})
    audit=pd.DataFrame(records)
    inventory_frame=pd.DataFrame([{'plantclef_name':k,'image_rows':v} for k,v in sorted(inventory.items())])
    unmatched=pd.DataFrame([{'plantclef_name':k,'image_rows':v} for k,v in sorted(unmapped.items())])
    organs=pd.DataFrame([{'species':sp,'organ':organ,'image_rows':count}
                        for (sp,organ),count in sorted(organ_counts.items())])
    return audit,inventory_frame,unmatched,organs


def extend_with_dataset_species(csv_path, regional_targets, national_lookup, ambiguous_names, chunksize=100000):
    """Include dataset species without claiming they occur (wild or cultivated) in Sicily."""
    names=set()
    for chunk in pd.read_csv(csv_path,sep=';',usecols=['species'],dtype=str,
                             keep_default_na=False,chunksize=chunksize):
        names.update(chunk.species.str.strip().unique())
    ambiguous=set(ambiguous_names.get('normalized_name',pd.Series(dtype=str)))
    lookup=dict(national_lookup)
    targets=set(regional_targets)
    unresolved=[]
    for name in sorted(names):
        key=norm(name)
        if not key or key in ambiguous:
            unresolved.append({'plantclef_name':name,'reason':'unparsed' if not key else 'ambiguous_taxonomy'})
            continue
        accepted=lookup.get(key)
        if accepted is None:
            accepted=species_name(name)
            lookup[key]=accepted
        targets.add(accepted)
    # Keep only names that can actually map to a chosen target.
    lookup={key:sp for key,sp in lookup.items() if sp in targets}
    return sorted(targets),lookup,pd.DataFrame(unresolved,columns=['plantclef_name','reason'])
