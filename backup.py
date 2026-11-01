"""Validate a credential-free portable backup before changing local state."""
from sync_store import SyncError

def validate_backup(d,valid):
    def fail():raise SyncError(400,'Bu geçerli bir Pocket Local yedeği değil.')
    if d.get('format')!='pocket-local-v1':fail()
    c=d.get('collection');t=d.get('trade')
    if not isinstance(c,dict) or not isinstance(t,dict):fail()
    clean={}
    for field in ('overrides','secondOverrides'):
        value=c.get(field,{})
        if not isinstance(value,dict) or any(k not in valid or type(v) is not bool for k,v in value.items()):fail()
        clean[field]=value.copy()
    q=c.get('quantities',{})
    if not isinstance(q,dict) or set(q)-{'main','second'}:fail()
    for a,values in q.items():
        if not isinstance(values,dict) or any(k not in valid or type(v) is not int or not 0<=v<=999999 for k,v in values.items()):fail()
        for k,v in values.items():clean['overrides' if a=='main' else 'secondOverrides'][k]=v>0
    clean['quantities']=q
    b=t.get('balances');selected=t.get('selected')
    if not isinstance(b,dict) or set(b)!={'main','second'} or any(v is not None and (type(v) is not int or not 0<=v<=10**9) for v in b.values()):fail()
    if type(b['main']) is not int or not isinstance(selected,list) or any(not isinstance(k,str) or k not in valid for k in selected):fail()
    # Saved plans are snapshots; validate rather than accepting arbitrary nested data.
    plan=t.get('plan')
    if plan is not None and not isinstance(plan,dict):fail()
    # Rebuild plans from current data in the UI after restoring; keep budgets/draft.
    return clean,{'revision':0,'balances':b,'selected':list(dict.fromkeys(selected)),'plan':None}
