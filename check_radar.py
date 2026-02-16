import ast
import pandas as pd
from collections import defaultdict

# Load dataset
df = pd.read_csv('python/data/dataset.csv')

# Extract categories with sentiments using FIXED parsing
cat_sent = defaultdict(lambda: {'Positivo': 0, 'Neutro': 0, 'Negativo': 0})

for idx, row in df.iterrows():
    try:
        cats_str = str(row['Categorias']).strip()
        if cats_str in ['[]', '{}', '', 'nan', 'None']:
            continue
        
        # Use ast.literal_eval for proper parsing
        cats_list = ast.literal_eval(cats_str)
        if not isinstance(cats_list, list):
            continue
        
        sentimiento = str(row['Sentimiento'])
        
        for cat in cats_list:
            if sentimiento in cat_sent[cat]:
                cat_sent[cat][sentimiento] += 1
    except:
        continue

# Filter categories with >5 total mentions
cat_sent_filtrado = {k: v for k, v in cat_sent.items() if sum(v.values()) > 5}

print(f'✅ FIXED PARSING RESULTS:')
print(f'Total unique categories: {len(cat_sent)}')
print(f'Categories with >5 mentions: {len(cat_sent_filtrado)}')
print(f'\nQualifying categories:')
for cat, sents in sorted(cat_sent_filtrado.items(), key=lambda x: sum(x[1].values()), reverse=True):
    total = sum(sents.values())
    print(f'  {cat}: {total} mentions (Pos:{sents["Positivo"]}, Neu:{sents["Neutro"]}, Neg:{sents["Negativo"]})')

print(f'\nExcluded (≤5 mentions):')
excluded = {k: v for k, v in cat_sent.items() if sum(v.values()) <= 5}
for cat, sents in sorted(excluded.items()):
    print(f'  {cat}: {sum(sents.values())} mentions')

print(f'\n{"✅ RADAR CHART CAN NOW BE GENERATED!" if len(cat_sent_filtrado) >= 4 else f"❌ Still cannot generate (need ≥4 with >5 mentions, have {len(cat_sent_filtrado)})"}')
