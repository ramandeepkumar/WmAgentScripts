#!/usr/bin/env python
from assignSession import *
from McMClient import McMClient
from utils import workflowInfo
import reqMgrClient
import setDatasetStatusDBS3


def invalidator(url, invalid_status='INVALID'):
    mcm = McMClient(dev=False)
    invalids = mcm.getA('invalidations',query='status=new')
    print len(invalids),"Object to be invalidated"
    for invalid in invalids:
        acknowledge= False
        if invalid['type'] == 'request':
            wfn = invalid['object']
            print "need to invalidate the workflow",wfn
            wfo = session.query(Workflow).filter(Workflow.name == wfn).first()
            if wfo:
                ## set forget of that thing (although checkor will recover from it)
                wfo.status = 'forget'
                session.commit()
            wfi = workflowInfo(url, wfn)
            success = "not rejected"
            if wfi.request['RequestStatus'] in ['assignment-approved','new','completed']:
                success = reqMgrClient.rejectWorkflow(url, wfn)
                pass
            else:
                success = reqMgrClient.abortWorkflow(url, wfn)
                pass
            print success
            acknowledge= True
        elif invalid['type'] == 'dataset':
            dataset = invalid['object']
            if 'None-' in dataset: continue
            if 'FAKE-' in dataset: continue
            print "setting",dataset,"to",invalid_status
            success = "not invalidated"
            success = setDatasetStatusDBS3.setStatusDBS3('https://cmsweb.cern.ch/dbs/prod/global/DBSWriter', dataset, invalid_status, None)
            print success
            ## make a delete request from everywhere we can find ?
            acknowledge= True
        else:
            print "\t\t",invalid['type']," type not recognized"

        if acknowledge:
            ## acknoldge invalidation in mcm, provided we can have the api
            print "No acknowledgment api yet available"
            #mcm.get('/restapi/invalidations/acknowledge/%s'%( invalid['_id'] ))

if __name__ == "__main__":
    url = 'cmsweb.cern.ch'
    invalidator(url)
