from pathlib import Path
import base64, zlib, csv, json, uuid, re, hashlib, itertools
ROOT=Path('/mnt/data/Orbit_Retail_PowerBI_Project'); NAME='Orbit_Retail_Sales_Analysis'
REP=ROOT/f'{NAME}.Report'; MOD=ROOT/f'{NAME}.SemanticModel'; DEF=MOD/'definition';TAB=DEF/'tables'; RDEF=REP/'definition'; PAGES=RDEF/'pages'
for p in [TAB,PAGES,REP/'StaticResources'/'SharedResources'/'BaseThemes',REP/'StaticResources'/'RegisteredResources']:
  p.mkdir(parents=True, exist_ok=True)
def dump(path,obj):
  path.parent.mkdir(parents=True,exist_ok=True)
  path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def shortid(tag): return hashlib.sha256(tag.encode()).hexdigest()[:20]
ROOT.joinpath('OPEN_IN_POWER_BI_DESKTOP.txt').write_text(
 'ORBIT RETAIL SALES ANALYSIS — OPEN THE POWER BI PROJECT\n\n'
 '1. Extract the entire ZIP first. Do not open just one file from inside the ZIP.\n'
 '2. On Windows with a current Power BI Desktop, double-click Orbit_Retail_Sales_Analysis.pbip.\n'
 '3. If prompted, Apply changes / Refresh to load the embedded sample tables.\n'
 '4. The model contains self-contained, compressed CSV extracts in Power Query M partitions: no web access or local file path is required.\n'
 '5. For a standard .pbix file, use File > Save As > Power BI Desktop file (.pbix).\n'
 '6. This project was generated outside Power BI Desktop: it passed structural/static checks, but a live Desktop rendering test was not possible.\n\n'
 'Alternative: open Dashboard_Preview.html in any modern browser for a self-contained interactive dashboard preview.\n',encoding='utf-8')
dump(ROOT/f'{NAME}.pbip',{'$schema':'https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json','version':'1.0','artifacts':[{'report':{'path':f'{NAME}.Report'}}],'settings':{'enableAutoRecovery':True}})
dump(REP/'definition.pbir',{'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json','version':'4.0','datasetReference':{'byPath':{'path':f'../{NAME}.SemanticModel'}}})
dump(MOD/'definition.pbism',{'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json','version':'4.2','settings':{'qnaEnabled':False}})
for kind,p in [('Report',REP),('SemanticModel',MOD)]:
  dump(p/'.platform',{'$schema':'https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json','metadata':{'type':kind,'displayName':f'ORBIT Retail — {kind}'},'config':{'version':'2.0','logicalId':str(uuid.uuid5(uuid.NAMESPACE_DNS,kind+NAME))}})
(DEF/'database.tmdl').write_text('database\n\tcompatibilityLevel: 1600\t\n\tcompatibilityMode: powerBI\n',encoding='utf-8')
TYPES={
'DimDates': [('Date','dateTime'),('Year','int64'),('Quarter','string'),('MonthNumber','int64'),('MonthName','string'),('YearMonth','string'),('YearMonthSort','int64'),('MonthStart','dateTime')],
'DimProducts': [('ProductID','int64'),('SKU','string'),('ProductName','string'),('Category','string'),('Subcategory','string'),('Brand','string'),('StandardPrice','double'),('UnitCost','double')],
'DimCustomers': [('CustomerID','int64'),('SignupDate','dateTime'),('CustomerType','string'),('CustomerSegment','string'),('AcquisitionSource','string')],
'DimRegions': [('RegionID','int64'),('Region','string')],
'DimChannels': [('ChannelID','int64'),('Channel','string')],
'FactSales': [('LineID','int64'),('OrderID','int64'),('OrderDate','dateTime'),('ProductID','int64'),('CustomerID','int64'),('RegionID','int64'),('ChannelID','int64'),('Quantity','int64'),('ReturnedQuantity','int64'),('UnitPrice','double'),('UnitCost','double'),('DiscountRate','double'),('GrossSales','double'),('DiscountAmount','double'),('SalesAfterDiscount','double'),('ReturnValue','double'),('COGS','double'),('ReturnedCOGS','double'),('NetSales','double'),('NetCOGS','double'),('GrossProfit','double'),('PromotionFlag','string')],
'FactTargets': [('MonthStart','dateTime'),('RegionID','int64'),('ChannelID','int64'),('SalesTarget','double'),('ProfitTarget','double')]
}
M_TYPES={'dateTime':'type date','int64':'Int64.Type','double':'type number','string':'type text'}
# Calculated display measures; all are defined on FactSales so PBIR projections have a single home.
MEASURES=[
 ('Gross Sales','SUM(FactSales[GrossSales])','€#,0;€-#,0','Revenue'),
 ('Discounts','SUM(FactSales[DiscountAmount])','€#,0;€-#,0','Revenue'),
 ('Returns Value','SUM(FactSales[ReturnValue])','€#,0;€-#,0','Returns'),
 ('Net Revenue','SUM(FactSales[NetSales])','€#,0;€-#,0','Revenue'),
 ('Net COGS','SUM(FactSales[NetCOGS])','€#,0;€-#,0','Profitability'),
 ('Gross Profit','SUM(FactSales[GrossProfit])','€#,0;€-#,0','Profitability'),
 ('Gross Margin %','DIVIDE([Gross Profit], [Net Revenue])','0.0%','Profitability'),
 ('Orders','DISTINCTCOUNT(FactSales[OrderID])','#,0','Customers'),
 ('Units Sold','SUM(FactSales[Quantity])','#,0','Revenue'),
 ('Returned Units','SUM(FactSales[ReturnedQuantity])','#,0','Returns'),
 ('Average Order Value','DIVIDE([Net Revenue], [Orders])','€#,0.00','Customers'),
 ('Customers','DISTINCTCOUNT(FactSales[CustomerID])','#,0','Customers'),
 ('Revenue per Customer','DIVIDE([Net Revenue], [Customers])','€#,0.00','Customers'),
 ('Return Rate %','DIVIDE([Returned Units], [Units Sold])','0.0%','Returns'),
 ('Return Value %','DIVIDE([Returns Value], [Gross Sales]-[Discounts])','0.0%','Returns'),
 ('Discount Rate %','DIVIDE([Discounts], [Gross Sales])','0.0%','Revenue'),
 ('Sales Target','SUM(FactTargets[SalesTarget])','€#,0;€-#,0','Targets'),
 ('Profit Target','SUM(FactTargets[ProfitTarget])','€#,0;€-#,0','Targets'),
 ('Sales Variance','[Net Revenue]-[Sales Target]','€#,0;€-#,0','Targets'),
 ('Sales Variance %','DIVIDE([Sales Variance],[Sales Target])','0.0%;-0.0%','Targets'),
 ('Target Attainment %','DIVIDE([Net Revenue],[Sales Target])','0.0%','Targets'),
 ('Revenue PY','CALCULATE([Net Revenue], SAMEPERIODLASTYEAR(DimDates[Date]))','€#,0;€-#,0','Time Intelligence'),
 ('Revenue YoY %','DIVIDE([Net Revenue]-[Revenue PY],[Revenue PY])','0.0%;-0.0%','Time Intelligence'),
 ('Revenue YTD','TOTALYTD([Net Revenue],DimDates[Date])','€#,0;€-#,0','Time Intelligence'),
 ('Revenue YTD PY','CALCULATE([Revenue YTD],SAMEPERIODLASTYEAR(DimDates[Date]))','€#,0;€-#,0','Time Intelligence'),
 ('Revenue YTD YoY %','DIVIDE([Revenue YTD]-[Revenue YTD PY],[Revenue YTD PY])','0.0%;-0.0%','Time Intelligence'),
 ('2026 YTD Revenue','CALCULATE([Net Revenue], DATESBETWEEN(DimDates[Date], DATE(2026,1,1), DATE(2026,9,30)))','€#,0;€-#,0','Portfolio Headlines'),
 ('2025 Comparable Revenue','CALCULATE([Net Revenue], DATESBETWEEN(DimDates[Date], DATE(2025,1,1), DATE(2025,9,30)))','€#,0;€-#,0','Portfolio Headlines'),
 ('2026 YTD Growth %','DIVIDE([2026 YTD Revenue]-[2025 Comparable Revenue],[2025 Comparable Revenue])','0.0%;-0.0%','Portfolio Headlines'),
]
# For self-contained portability, compress CSV tables into in-memory embedded Power Query binary payloads.
for table,columns in TYPES.items():
  raw=(ROOT/'Data'/f'{table}.csv').read_bytes()
  packed=base64.b64encode(zlib.compress(raw,9)).decode('ascii')
  assert zlib.decompress(base64.b64decode(packed))==raw
  names=[n for n,_ in columns]
  type_expr=', '.join('{'+'"'+n+'", '+M_TYPES[t]+'}' for n,t in columns)
  # base64 can be on a single M-string; line wrapping done by M engine on UI.
  m=[
    'let',
    '    CompressedCSV = Binary.FromText("'+packed+'", BinaryEncoding.Base64),',
    '    Source = Csv.Document(Binary.Decompress(CompressedCSV, Compression.Deflate), [Delimiter=",", Columns='+str(len(columns))+', Encoding=65001, QuoteStyle=QuoteStyle.Csv]),',
    '    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),',
    '    Typed = Table.TransformColumnTypes(Headers, {'+type_expr+'}, "en-US")',
    'in',
    '    Typed'
  ]
  out=['table '+table, '\tlineageTag: '+str(uuid.uuid5(uuid.NAMESPACE_DNS,NAME+table)),'']
  for col,typ in columns:
    out+=['\tcolumn '+col,'\t\tdataType: '+typ,'\t\tsummarizeBy: none','\t\tsourceColumn: '+col,'\t\tlineageTag: '+str(uuid.uuid5(uuid.NAMESPACE_DNS,NAME+table+col)),'']
  if table=='FactSales':
    for label,expression,formatting,folder in MEASURES:
      # Display folders organize fields in Power BI desktop.
      out+=['\tmeasure \''+label+'\' = '+expression,'\t\tformatString: '+formatting,'\t\tdisplayFolder: '+folder,'\t\tlineageTag: '+str(uuid.uuid5(uuid.NAMESPACE_DNS,NAME+label)),'']
  out+=['\tpartition '+table+' = m','\t\tmode: import','\t\tsource =']
  out+=['\t\t\t'+s for s in m]
  out+=['','\tannotation PBI_NavigationStepName = Navigation','\tannotation PBI_ResultType = Table']
  (TAB/f'{table}.tmdl').write_text('\n'.join(out)+'\n',encoding='utf-8')
refs=['model Model','\tculture: en-US','\tdefaultPowerBIDataSourceVersion: powerBI_V3','\tdiscourageImplicitMeasures']
refs=['model Model','\tculture: en-US','\tdefaultPowerBIDataSourceVersion: powerBI_V3','\tdiscourageImplicitMeasures: true','']+['ref table '+t for t in TYPES]
(DEF/'model.tmdl').write_text('\n'.join(refs)+'\n',encoding='utf-8')
rels=[('FactSales','OrderDate','DimDates','Date'),('FactSales','ProductID','DimProducts','ProductID'),('FactSales','CustomerID','DimCustomers','CustomerID'),('FactSales','RegionID','DimRegions','RegionID'),('FactSales','ChannelID','DimChannels','ChannelID'),('FactTargets','MonthStart','DimDates','Date'),('FactTargets','RegionID','DimRegions','RegionID'),('FactTargets','ChannelID','DimChannels','ChannelID')]
out=[]
for a,ac,b,bc in rels:
 out += ['relationship '+shortid(a+ac+b+bc),'\tfromColumn: '+a+'.'+ac,'\ttoColumn: '+b+'.'+bc,'']
(DEF/'relationships.tmdl').write_text('\n'.join(out),encoding='utf-8')
# Visual JSON authoring: Power BI Enhanced Report format (PBIR).
SCHEMA='https://developer.microsoft.com/json-schemas/fabric/item/report/definition/'
def lit(value):
  if isinstance(value,bool): v='true' if value else 'false'
  elif isinstance(value,int): v=f'{value}L'
  elif isinstance(value,float): v=f'{value}D'
  else: v="'"+str(value).replace("'","''")+"'"
  return {'expr':{'Literal':{'Value':v}}}
def col(table,field): return {'Column':{'Expression':{'SourceRef':{'Entity':table}},'Property':field}}
def measure(field): return {'Measure':{'Expression':{'SourceRef':{'Entity':'FactSales'}},'Property':field}}
def proj(kind,table,name,caption=None,active=False):
  return {'field':col(table,name) if kind=='column' else measure(name), 'queryRef':f'{table}.{name}', 'nativeQueryRef':name,**({'displayName':caption} if caption else {}),**({'active':True} if active else {})}
def format_shell(title):
  return {
   'title':[{'properties':{'show':lit(True),'text':lit(title),'fontSize':lit(12),'fontColor':{'solid':{'color':lit('#17304A')}}}}],
   'background':[{'properties':{'show':lit(True),'color':{'solid':{'color':lit('#FFFFFF')}},'transparency':lit(0)}}],
   'border':[{'properties':{'show':lit(True),'color':{'solid':{'color':lit('#E6EDF2')}}}}]
  }
TABS=[]
PAGE_META=[
('Executive Summary','Board-level overview | commercial health & target delivery'),
('Sales Trends','Revenue seasonality, growth and business mix'),
('Products & Margin','Category performance, margin and product exposure'),
('Customers & Channels','Customer segments, acquisition and channel economics'),
('Targets & Returns','Variance against plan, returns and leakage analysis')]
for idx,(label,subtitle) in enumerate(PAGE_META):
  pid=shortid('page'+str(idx)+NAME);TABS.append(pid)
  pd=PAGES/pid;pd.mkdir(parents=True,exist_ok=True)
  dump(pd/'page.json',{'$schema':SCHEMA+'page/2.1.0/schema.json','name':pid,'displayName':label,'displayOption':'FitToPage','height':720,'width':1280})
  def put(ident,visual):
    name=shortid(pid+ident)
    dump(pd/'visuals'/name/'visual.json',{'$schema':SCHEMA+'visualContainer/2.7.0/schema.json','name':name,**visual})
  def textbox(ident,txt,x,y,w,h,size=24,color='#102941',weight='bold'):
    put(ident,{'position':{'x':x,'y':y,'z':1000,'width':w,'height':h,'tabOrder':0},'visual':{'visualType':'textbox', 'objects':{'general':[{'properties':{'paragraphs':[{'textRuns':[{'value':txt,'textStyle':{'fontFamily':'Segoe UI','fontSize':f'{size}pt','fontWeight':weight,'color':color}}],'horizontalTextAlignment':'left'}]}}]},'visualContainerObjects':{'background':[{'properties':{'show':lit(False)}}],'border':[{'properties':{'show':lit(False)}}]},'drillFilterOtherVisuals':False}})
  def chart(ident,typ,title,x,y,w,h,roles,sort=None):
    state={role:{'projections':[proj(kind,t,n,active=(kind=='column' and typ not in ('tableEx',))) for kind,t,n in fields]} for role,fields in roles.items()}
    q={'queryState':state}
    if sort:
      key=measure(sort[1]) if sort[0]=='measure' else col(sort[0],sort[1]);q['sortDefinition']={'sort':[{'field':key,'direction':sort[2]}],'isDefaultSort':True}
    put(ident,{'position':{'x':x,'y':y,'z':3,'width':w,'height':h,'tabOrder':0},'visual':{'visualType':typ,'query':q,'objects':{},'visualContainerObjects':format_shell(title),'drillFilterOtherVisuals':True}})
  def kpi(ident,title,field,x,y,w=229):
    chart(ident,'cardVisual',title,x,y,w,116,{'Data':[('measure','FactSales',field)]})
  def title_main():
    textbox('head',f'ORBIT / {label.upper()}',30,19,870,47,24)
    textbox('sub',subtitle+'   ·   2024—Sep 2026   ·   Synthetic portfolio data',31,70,1070,24,10,'#687A8F','normal')
    chart('yearFilter','slicer','YEAR',1090,18,156,73,{'Values':[('column','DimDates','Year')]})
  def cc(f):return ('column',f[0],f[1])
  def mm(s):return ('measure','FactSales',s)
  title_main()
  if idx==0:
    for i,(ttl,metric) in enumerate([('NET REVENUE','Net Revenue'),('GROSS PROFIT','Gross Profit'),('GROSS MARGIN','Gross Margin %'),('ORDERS','Orders'),('VS. PLAN','Sales Variance %')]):kpi('kpi'+str(i),ttl,metric,30+i*248,111,235)
    chart('trend','lineChart','REVENUE & TARGET / MONTH',30,244,750,246,{'Category':[cc(('DimDates','YearMonth'))],'Y':[mm('Net Revenue'),mm('Sales Target')]})
    chart('channel','donutChart','SALES BY CHANNEL',796,244,452,246,{'Category':[cc(('DimChannels','Channel'))],'Y':[mm('Net Revenue')]})
    chart('region','clusteredBarChart','REVENUE BY REGION',30,503,598,193,{'Category':[cc(('DimRegions','Region'))],'Y':[mm('Net Revenue')]})
    chart('cats','tableEx','CATEGORY SCORECARD',644,503,604,193,{'Values':[cc(('DimProducts','Category')),mm('Net Revenue'),mm('Gross Margin %'),mm('Returns Value')]})
  elif idx==1:
    for i,(ttl,metric) in enumerate([('2026 YTD REVENUE','2026 YTD Revenue'),('2025 SAME PERIOD','2025 Comparable Revenue'),('2026 YTD GROWTH','2026 YTD Growth %'),('AVERAGE ORDER','Average Order Value'),('DISCOUNT RATE','Discount Rate %')]): kpi('kpi'+str(i),ttl,metric,30+i*248,111,235)
    chart('growth','lineChart','NET SALES TREND / BY MONTH',30,244,760,276,{'Category':[cc(('DimDates','YearMonth'))],'Y':[mm('Net Revenue'),mm('Revenue PY')]})
    chart('region','clusteredColumnChart','REGIONAL MIX',808,244,440,276,{'Category':[cc(('DimRegions','Region'))],'Y':[mm('Net Revenue')]})
    chart('channel','clusteredBarChart','CHANNEL SALES',30,535,600,160,{'Category':[cc(('DimChannels','Channel'))],'Y':[mm('Net Revenue'),mm('Gross Profit')]})
    chart('metrics','tableEx','SALES PERFORMANCE DETAIL',646,535,602,160,{'Values':[cc(('DimDates','YearMonth')),mm('Net Revenue'),mm('Orders'),mm('Average Order Value')]})
  elif idx==2:
    for i,(ttl,metric) in enumerate([('GROSS PROFIT','Gross Profit'),('MARGIN %','Gross Margin %'),('RETURN RATE','Return Rate %'),('UNITS SOLD','Units Sold'),('DISCOUNTS','Discounts')]):kpi('kpi'+str(i),ttl,metric,30+i*248,111,235)
    chart('bycategory','clusteredBarChart','CATEGORY CONTRIBUTION',30,244,608,243,{'Category':[cc(('DimProducts','Category'))],'Y':[mm('Net Revenue'),mm('Gross Profit')]})
    chart('return','clusteredColumnChart','RETURN VALUE BY CATEGORY',653,244,595,243,{'Category':[cc(('DimProducts','Category'))],'Y':[mm('Returns Value')]})
    chart('products','tableEx','PRODUCT PERFORMANCE / REVENUE & MARGIN',30,503,780,193,{'Values':[cc(('DimProducts','ProductName')),mm('Net Revenue'),mm('Gross Profit'),mm('Gross Margin %'),mm('Returned Units')]})
    chart('margin','clusteredBarChart','MARGIN BY PRODUCT CATEGORY',825,503,423,193,{'Category':[cc(('DimProducts','Category'))],'Y':[mm('Gross Margin %')]})
  elif idx==3:
    for i,(ttl,metric) in enumerate([('ACTIVE CUSTOMERS','Customers'),('REVENUE / CUSTOMER','Revenue per Customer'),('AVERAGE ORDER VALUE','Average Order Value'),('ORDERS','Orders'),('NET REVENUE','Net Revenue')]):kpi('kpi'+str(i),ttl,metric,30+i*248,111,235)
    chart('cust','clusteredBarChart','REVENUE BY CUSTOMER SEGMENT',30,244,600,242,{'Category':[cc(('DimCustomers','CustomerSegment'))],'Y':[mm('Net Revenue')]})
    chart('acq','clusteredBarChart','CUSTOMER ACQUISITION SOURCE',647,244,601,242,{'Category':[cc(('DimCustomers','AcquisitionSource'))],'Y':[mm('Customers')]})
    chart('chan','tableEx','CHANNEL PERFORMANCE',30,502,605,194,{'Values':[cc(('DimChannels','Channel')),mm('Net Revenue'),mm('Orders'),mm('Gross Margin %')]})
    chart('region','clusteredBarChart','ORDER VALUE BY REGION',650,502,598,194,{'Category':[cc(('DimRegions','Region'))],'Y':[mm('Average Order Value')]})
  elif idx==4:
    for i,(ttl,metric) in enumerate([('NET REVENUE','Net Revenue'),('SALES TARGET','Sales Target'),('VARIANCE %','Sales Variance %'),('RETURN VALUE','Returns Value'),('RETURNS / SALES','Return Value %')]):kpi('kpi'+str(i),ttl,metric,30+i*248,111,235)
    chart('trend','lineChart','ACTUAL VS PLAN / MONTH',30,244,761,270,{'Category':[cc(('DimDates','YearMonth'))],'Y':[mm('Net Revenue'),mm('Sales Target')]})
    chart('region','clusteredBarChart','TARGET ATTAINMENT BY REGION',806,244,442,270,{'Category':[cc(('DimRegions','Region'))],'Y':[mm('Target Attainment %')]})
    chart('returns','clusteredColumnChart','REFUND EXPOSURE BY CATEGORY',30,531,601,164,{'Category':[cc(('DimProducts','Category'))],'Y':[mm('Returns Value')]})
    chart('targets','tableEx','TARGET VARIANCE / CHANNEL',646,531,602,164,{'Values':[cc(('DimChannels','Channel')),mm('Net Revenue'),mm('Sales Target'),mm('Sales Variance %')]})
dump(PAGES/'pages.json',{'$schema':SCHEMA+'pagesMetadata/1.0.0/schema.json','pageOrder':TABS,'activePageName':TABS[0]})
dump(RDEF/'version.json',{'$schema':SCHEMA+'versionMetadata/1.0.0/schema.json','version':'2.0.0'})
# The bundled theme is intentionally lightweight. No personal data or cloud connectivity.
THEME={'name':'ORBIT Calm Analytics','dataColors':['#2463EB','#14B8A6','#F5A524','#7C6FEE','#FB7185','#4C83A8'],'background':'#F4F7FB','foreground':'#17304A','tableAccent':'#2463EB','visualStyles':{}}
dump(REP/'StaticResources'/'SharedResources'/'BaseThemes'/'CY26SU02.json',THEME)
dump(RDEF/'report.json',{
 '$schema':SCHEMA+'report/3.2.0/schema.json',
 'themeCollection':{'baseTheme':{'name':'CY26SU02','reportVersionAtImport':{'visual':'2.7.0','report':'3.2.0','page':'2.1.0'},'type':'SharedResources'}},
 'filterConfig':{'filters':[]},'settings':{'defaultDrillFilterOtherVisuals':True},
 'resourcePackages':[{'name':'SharedResources','type':'SharedResources','items':[{'name':'CY26SU02','path':'BaseThemes/CY26SU02.json','type':'BaseTheme'}]}]})
# Secondary analyst artifacts: DAX catalog, schema and star model explanation.
(ROOT/'DAX_Measures.dax').write_text('/* ORBIT Retail | Power BI DAX metric catalog — measures are already in FactSales.tmdl */\n\n'+ '\n\n'.join(f"{name} = {expr}\n-- Format: {fmt} | Folder: {folder}" for name,expr,fmt,folder in MEASURES)+'\n',encoding='utf-8')
(ROOT/'Power_Query_Notes.md').write_text('''# Power Query ETL / ELT notes

The seven CSV files in `Data/` are reproducible source exports. The Power BI semantic model embeds compressed copies so the project is portable without Windows-specific paths.

Each table is imported via Power Query M:

```powerquery
let
    CompressedCSV = Binary.FromText("<base64-compressed CSV>", BinaryEncoding.Base64),
    Source = Csv.Document(Binary.Decompress(CompressedCSV, Compression.Deflate), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, { /* typed columns */ }, "en-US")
in
    Typed
```

Transformation steps: load CSV bytes → decompress → parse CSV → promote headers → set dates, whole numbers, currency-like numerics and text. This is a **portable sample snapshot**, not an automatic connection to a live retailer. To swap data, replace the partition query with CSV/database imports, retaining the column names and star-schema keys.
''',encoding='utf-8')
model={'tables':{t:[a for a,b in c] for t,c in TYPES.items()},'relationships':[{'fact_table':a,'fact_key':ac,'dimension_table':b,'dimension_key':bc,'cross_filter':'single','cardinality':'many-to-one'} for a,ac,b,bc in rels], 'business_definitions':{'Net Revenue':'Gross sales – discounts – allocated returns','Gross Profit':'Net revenue – cost of goods sold on non-returned units','Gross Margin %':'Gross profit / net revenue','Return Rate %':'Returned units / sold units','Sales Variance %':'(net revenue – monthly target) / monthly target','Orders':'Distinct OrderID across filtered sales rows','Net Revenue Attribution':'Return value attributed to original sale month, not refund processing date'}}
dump(ROOT/'MODEL_DICTIONARY.json',model)
# Static validations for generated report/model definitions.
js=list(REP.rglob('*.json'))+list(MOD.rglob('*.json'))
for p in js:json.loads(p.read_text(encoding='utf-8'))
allids=[]
for p in (RDEF/'pages').rglob('visual.json'):
 o=json.loads(p.read_text());assert len(o['name'])==20;allids.append(o['name']);assert o['position']['x']+o['position']['width']<=1280
assert len(set(allids))==len(allids)
assert len(list((RDEF/'pages').rglob('visual.json')))==len(allids)
print('PBIP ready','7 tables',len(MEASURES),'measures',len(rels),'relationships',len(TABS),'pages',len(allids),'visuals','model MB',round(sum(p.stat().st_size for p in TAB.glob('*.tmdl'))/1e6,2))
