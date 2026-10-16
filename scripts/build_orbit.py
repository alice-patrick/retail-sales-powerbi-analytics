from __future__ import annotations
import os, csv, random, math, json, calendar, datetime as dt, statistics, collections
from pathlib import Path
R=random.Random(20261016)
ROOT=Path('/mnt/data/Orbit_Retail_PowerBI_Project'); DATA=ROOT/'Data'; DATA.mkdir(parents=True,exist_ok=True)
CATS={
 'Electronics': [('Audio', ['Wireless Earbuds','Noise-Cancelling Headphones','Bluetooth Speaker','Soundbar']),('Computing', ['USB-C Hub','Mechanical Keyboard','Portable SSD','Wireless Mouse']),('Mobile', ['Fast Charger','Power Bank','Smartwatch','Phone Stand'])],
 'Home & Living': [('Kitchen', ['Air Fryer','Coffee Grinder','Kettle','Blender']),('Decor', ['Desk Lamp','Ceramic Vase','Throw Blanket','Wall Clock']),('Storage', ['Storage Baskets','Drawer Organiser','Shelf Set','Shoe Rack'])],
 'Sports & Outdoors': [('Fitness', ['Yoga Mat','Adjustable Dumbbells','Resistance Bands','Foam Roller']),('Outdoor', ['Insulated Bottle','Camping Lantern','Daypack','Portable Chair']),('Cycling', ['Bike Light','Cycling Gloves','Helmet','Bike Lock'])],
 'Beauty & Wellness': [('Skincare', ['Face Cleanser','Hydrating Serum','Moisturiser','Sunscreen']),('Personal Care', ['Hair Dryer','Electric Trimmer','Body Lotion','Travel Kit']),('Wellness', ['Diffuser','Eye Mask','Massage Roller','Heat Pad'])]
}
brands=['Astra','Pavo','Nori','Elm','Solstice','North','Arden','Aven','Pulse','Bello']
price_range={'Electronics':(32,329),'Home & Living':(16,179),'Sports & Outdoors':(12,189),'Beauty & Wellness':(9,105)}
margin_base={'Electronics':.285,'Home & Living':.47,'Sports & Outdoors':.425,'Beauty & Wellness':.575}
products=[]; pid=1001
for cat,subgroups in CATS.items():
  for sub, names in subgroups:
    for name in names:
      for tier in ['Core','Plus']:
        low,high=price_range[cat]; p=round(R.uniform(low,high)*(.76 if tier=='Core' else 1.2),2)
        margin=max(.18,min(.65,margin_base[cat]+R.uniform(-.075,.065)))
        cost=round(p*(1-margin),2)
        products.append(dict(ProductID=pid,SKU=f'OR-{pid}',ProductName=f'{name} {tier}',Category=cat,Subcategory=sub,Brand=R.choice(brands),StandardPrice=f'{p:.2f}',UnitCost=f'{cost:.2f}'))
        pid+=1
reg=[(1,'Attica',.47),(2,'Northern Greece',.24),(3,'Central Greece',.17),(4,'Islands & South',.12)]
chs=[(1,'Online',.47),(2,'Retail Stores',.36),(3,'Marketplace',.17)]
regions=[{'RegionID':x,'Region':y} for x,y,_ in reg]
channels=[{'ChannelID':x,'Channel':y} for x,y,_ in chs]
start=dt.date(2024,1,1); end=dt.date(2026,9,30)
month_names=['January','February','March','April','May','June','July','August','September','October','November','December']
cal=[]; day=start
while day<=end:
  cal.append(dict(Date=day.isoformat(),Year=day.year,Quarter=f'Q{((day.month-1)//3)+1}',MonthNumber=day.month,MonthName=month_names[day.month-1],YearMonth=day.strftime('%Y-%m'),YearMonthSort=day.year*100+day.month,MonthStart=day.replace(day=1).isoformat()))
  day+=dt.timedelta(days=1)
# Members join throughout the historical period; only eligible customers purchase on a given date.
customers=[]
for i in range(1,3601):
  join=dt.date(2023,1,1)+dt.timedelta(days=R.randint(0,(end-dt.date(2023,1,1)).days))
  typ=R.choices(['Consumer','Small Business'],weights=[.86,.14])[0]
  seg=R.choices(['Value','Regular','Premium'],weights=[.41,.43,.16])[0]
  source=R.choices(['Organic Search','Paid Search','Social','Referral','In-store'],weights=[.27,.23,.16,.15,.19])[0]
  customers.append(dict(CustomerID=i,SignupDate=join.isoformat(),CustomerType=typ,CustomerSegment=seg,AcquisitionSource=source))
customers.sort(key=lambda c:c['SignupDate'])
# Sample order volume with growth, seasonality, regional differences, and evolving channel mix.
season={1:.83,2:.88,3:.96,4:1.01,5:1.05,6:1.06,7:1.13,8:1.11,9:1.03,10:1.07,11:1.36,12:1.52}
rows=[]; line_id=1; order_id=200000
pweights=[1.12 if p['Category']=='Beauty & Wellness' else .94 if p['Category']=='Electronics' else 1.0 for p in products]
# Precomputed daily series to avoid zero-order weekends; deterministic sample.
day=start
while day<=end:
  base={2024:25.8,2025:37.2,2026:46.8}[day.year]
  wk=1.20 if day.weekday() in (5,6) else .94
  expected=base*season[day.month]*wk
  n=max(3,int(R.gauss(expected, math.sqrt(expected)*.55)))
  elig=[c for c in customers if c['SignupDate']<=day.isoformat()]
  for _ in range(n):
    order_id+=1
    cus=R.choice(elig)
    # highest distribution Attica; summer Island share increases
    rw=[w*(1.8 if day.month in [6,7,8] and x==4 else 1) for x,_,w in reg]
    rid=R.choices([x for x,_,w in reg],weights=rw)[0]
    cw=[w*(1.17 if day.year==2026 and x==1 else 1) for x,_,w in chs]
    cid=R.choices([x for x,_,w in chs],weights=cw)[0]
    lines=R.choices([1,2,3],[.77,.20,.03])[0]
    chosen=R.sample(products,lines)
    promo=R.random()<(.36 if day.month in (11,12) else .20)
    for p in chosen:
      qty=R.choices([1,2,3,4],[.73,.21,.05,.01])[0]
      unit_price=float(p['StandardPrice'])
      unit_cost=float(p['UnitCost'])
      discount_rate=R.choice([.05,.10,.15,.20]) if promo else (R.choice([.03,.05]) if R.random()<.09 else 0)
      # Marketplace carries more promotion/return pressure.
      if cid==3 and promo: discount_rate=min(.25,discount_rate+.03)
      gross=round(qty*unit_price,2)
      discount=round(gross*discount_rate,2)
      pre_net=round(gross-discount,2)
      cogs=round(qty*unit_cost,2)
      cat=p['Category']; return_prob={'Electronics':.073,'Home & Living':.044,'Sports & Outdoors':.038,'Beauty & Wellness':.029}[cat]
      if cid==3: return_prob+=.018
      if cid==2: return_prob-=.006
      returned_qty=R.randint(1,qty) if R.random()<return_prob and day<=end-dt.timedelta(days=14) else 0
      # return value allocated to original order date; latest fortnight censored.
      rvalue=round(pre_net*returned_qty/qty,2) if returned_qty else 0
      rcogs=round(unit_cost*returned_qty,2)
      net=round(pre_net-rvalue,2)
      netcost=round(cogs-rcogs,2)
      gp=round(net-netcost,2)
      rows.append(dict(LineID=line_id,OrderID=order_id,OrderDate=day.isoformat(),ProductID=p['ProductID'],CustomerID=cus['CustomerID'],RegionID=rid,ChannelID=cid,Quantity=qty,ReturnedQuantity=returned_qty,UnitPrice=f'{unit_price:.2f}',UnitCost=f'{unit_cost:.2f}',DiscountRate=f'{discount_rate:.3f}',GrossSales=f'{gross:.2f}',DiscountAmount=f'{discount:.2f}',SalesAfterDiscount=f'{pre_net:.2f}',ReturnValue=f'{rvalue:.2f}',COGS=f'{cogs:.2f}',ReturnedCOGS=f'{rcogs:.2f}',NetSales=f'{net:.2f}',NetCOGS=f'{netcost:.2f}',GrossProfit=f'{gp:.2f}',PromotionFlag='Yes' if promo else 'No'))
      line_id+=1
  day+=dt.timedelta(days=1)
# Monthly store-region-channel budgets follow top-down forward plans, not booked sales.
# Calibrate annual budget on 2024 base expected volume and predefined growth assumptions.
# Scale by combination market/channel expectations; not drawn from realized rows.
base_avg_basket=sum(float(p['StandardPrice']) for p in products)/len(products)*1.14*1.15
bench_channel={1:1.0,2:1.10,3:.84}
bench_region={1:1.0,2:.91,3:.86,4:1.12}
monthly_targets=[]
for y in [2024,2025,2026]:
  lastmonth=9 if y==2026 else 12
  for m in range(1,lastmonth+1):
    days=calendar.monthrange(y,m)[1]
    plan_orders=({2024:27.0,2025:35.2,2026:44.5}[y])*days*season[m]
    for rid,region,rs in reg:
      adj_region=rs*(1.6 if rid==4 and m in [6,7,8] else 1)
      norm_region=sum(rw*(1.6 if rrid==4 and m in [6,7,8] else 1) for rrid,_,rw in reg)
      for cid,channel,cs in chs:
        cw=cs*(1.12 if y==2026 and cid==1 else 1)
        cw_tot=sum(ww*(1.12 if y==2026 and ci==1 else 1) for ci,_,ww in chs)
        multiplier=bench_channel[cid]*bench_region[rid]
        target=round(plan_orders*adj_region/norm_region*cw/cw_tot*base_avg_basket*multiplier*1.18,2)
        profit_target=round(target*(.355)*(.89 if cid==3 else 1.04 if cid==2 else 1),2)
        monthly_targets.append(dict(MonthStart=f'{y}-{m:02d}-01',RegionID=rid,ChannelID=cid,SalesTarget=f'{target:.2f}',ProfitTarget=f'{profit_target:.2f}'))

def write_csv(filename, records):
    p=DATA/filename
    with p.open('w',encoding='utf-8',newline='') as f:
      w=csv.DictWriter(f,fieldnames=list(records[0].keys()));w.writeheader();w.writerows(records)
    return p
paths={
 'FactSales': write_csv('FactSales.csv',rows),
 'FactTargets': write_csv('FactTargets.csv',monthly_targets),
 'DimProducts': write_csv('DimProducts.csv',products),
 'DimCustomers': write_csv('DimCustomers.csv',customers),
 'DimRegions': write_csv('DimRegions.csv',regions),
 'DimChannels': write_csv('DimChannels.csv',channels),
 'DimDates': write_csv('DimDates.csv',cal),
}
print('csv created',[(k,round(v.stat().st_size/1024)) for k,v in paths.items()])
# Verify referential integrity and component consistency.
keysets={
 'ProductID':{int(p['ProductID']) for p in products},
 'CustomerID':{int(c['CustomerID']) for c in customers},
 'RegionID':{x['RegionID'] for x in regions},
 'ChannelID':{x['ChannelID'] for x in channels},
 'OrderDate':{d['Date'] for d in cal}
}
for row in rows:
  for key,values in keysets.items(): assert row[key] in values,(key,row[key])
  assert int(row['ReturnedQuantity'])<=int(row['Quantity'])
  assert abs((float(row['GrossSales'])-float(row['DiscountAmount'])-float(row['ReturnValue']))-float(row['NetSales']))<.011
  assert abs(float(row['NetSales'])-float(row['NetCOGS'])-float(row['GrossProfit']))<.011
assert len({x['LineID'] for x in rows})==len(rows)
assert len({(x['MonthStart'],x['RegionID'],x['ChannelID']) for x in monthly_targets})==len(monthly_targets)
order_set={r['OrderID'] for r in rows}; gross=sum(float(r['GrossSales']) for r in rows); disc=sum(float(r['DiscountAmount']) for r in rows); refund=sum(float(r['ReturnValue']) for r in rows); net=sum(float(r['NetSales']) for r in rows); gp=sum(float(r['GrossProfit']) for r in rows)
assert abs(gross-disc-refund-net)<.1
print('Total orders',len(order_set),'lines',len(rows),'Net',round(net,2),'Margin',round(gp/net,4),'Targets',len(monthly_targets))
# Preaggregate for interactive self-contained preview and credible business insights.
product_by={int(p['ProductID']):p for p in products}
region_by={x['RegionID']:x['Region'] for x in regions}
channel_by={x['ChannelID']:x['Channel'] for x in channels}
agg=collections.defaultdict(lambda:collections.defaultdict(float))
for row in rows:
  key=(row['OrderDate'][:7],region_by[row['RegionID']],channel_by[row['ChannelID']],product_by[row['ProductID']]['Category'])
  x=agg[key]
  for sk in ['GrossSales','NetSales','GrossProfit','ReturnValue','DiscountAmount','Quantity','ReturnedQuantity']:x[sk]+=float(row[sk])
  x['LineCount']+=1
  x['Orders'].add(row['OrderID']) if isinstance(x.get('Orders'),set) else x.__setitem__('Orders',{row['OrderID']})
# Never sum distinct Orders across category for accurate grand-total AOV.
agg_rows=[]
for (month,region,channel,category),metrics in agg.items():
  agg_rows.append(dict(month=month,region=region,channel=channel,category=category,
   net=round(metrics['NetSales'],2),gp=round(metrics['GrossProfit'],2),refund=round(metrics['ReturnValue'],2),gross=round(metrics['GrossSales'],2),discount=round(metrics['DiscountAmount'],2),units=int(metrics['Quantity']),returned=int(metrics['ReturnedQuantity']),lines=int(metrics['LineCount'])))
agg_rows.sort(key=lambda x:(x['month'],x['region'],x['channel'],x['category']))
monthly=collections.defaultdict(lambda:dict(net=0.,gp=0.,refund=0.,gross=0.,discount=0.,units=0,returned=0,orders=set()))
for row in rows:
  d=monthly[row['OrderDate'][:7]]
  for k,field in [('net','NetSales'),('gp','GrossProfit'),('refund','ReturnValue'),('gross','GrossSales'),('discount','DiscountAmount')]: d[k]+=float(row[field])
  d['units']+=row['Quantity'];d['returned']+=row['ReturnedQuantity'];d['orders'].add(row['OrderID'])
monthly_rows=[{**{k:round(v,2) if isinstance(v,float) else len(v) if isinstance(v,set) else v for k,v in val.items()},'month':m} for m,val in sorted(monthly.items())]
byyear={}
for y in [2024,2025,2026]:
  rr=[r for r in rows if r['OrderDate'][:4]==str(y)]
  byyear[y]={'net':round(sum(float(r['NetSales']) for r in rr),2),'gross_profit':round(sum(float(r['GrossProfit']) for r in rr),2),'orders':len({r['OrderID'] for r in rr}), 'returns':round(sum(float(r['ReturnValue']) for r in rr),2)}
for y in byyear: byyear[y]['margin_pct']=round(100*byyear[y]['gross_profit']/byyear[y]['net'],2)
summary={'brand':'ORBIT Retail','generated_at':'2026-10-16','synthetic':True,'period':'2024-01-01 through 2026-09-30','orders':len(order_set),'lines':len(rows),'customers':len(customers),'products':len(products),'net_sales':round(net,2),'gross_profit':round(gp,2),'gross_margin_pct':round(gp/net*100,2),'return_value':round(refund,2),'discount_value':round(disc,2),'year':byyear,'monthly':monthly_rows,'preview_aggregates':agg_rows, 'targets':monthly_targets}
(ROOT/'analysis_results.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8')
(ROOT/'data_quality_report.json').write_text(json.dumps({'result':'PASS','checks':['All sales dimension keys valid','No duplicate LineID','No duplicate target grain keys','No returned quantity exceeding ordered quantity','Net sales = gross sales - discounts - refunds within €0.01','Gross profit = net sales - net cost within €0.01','No sales outside Date dimension','Customer signup never after order date','Returned quantity and monetary identities validated'],'sales_rows':len(rows),'target_rows':len(monthly_targets)},indent=2),encoding='utf-8')
# signup not after order, checked above by construction; negative profits may occur from discounted electronics, allowed in reality.
print('2026 year',byyear[2026])
