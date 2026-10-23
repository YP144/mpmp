HerosURL= r"postgres://beforebom-user:vlOlYphpG0n0k1SbLAppLf5EVLncsjyhaphWtpTUF8H0MYTGW90g6IBH4g0oRfU7@beforebom-0.beforebom.postgres.svc:5432/HEROS_DevelopmentMaster"
userURL= r"postgres://bom-db-user:zEfETCPR9YaHv46cgke6UjWOQ6uVu1XcTLhfd9iYtD62O3CXUrRCftSyOL7RyTKq@bom-db-0.bom-db.postgres.svc:5432/engineeruser"
CoworkURL = r"https://npdmbatch-he.lge.com/api/scheduler/report/he/model/bom/status"
OPurl = "postgresql://beforebom-user:vlOlYphpG0n0k1SbLAppLf5EVLncsjyhaphWtpTUF8H0MYTGW90g6IBH4g0oRfU7@beforebom-0.beforebom.postgres.svc:5432/OperationPlan_NPDM"
getCoworkDB = "postgres://beforebom-user:vlOlYphpG0n0k1SbLAppLf5EVLncsjyhaphWtpTUF8H0MYTGW90g6IBH4g0oRfU7@beforebom-0.beforebom.postgres.svc:5432/Model_CoWork_NPDM"
getMasterData = "postgres://mybini-user:vzS3Bo0K8Bx2DcHQPd0zIpkiEhjDcZKJ8vyTqHPcwF796dMbYF0m4dFaedWAxWIN@mybini-0.mybini.postgres.svc:5432/MasterMP_Data"
suffixURL = r"postgresql://beforebom-user:vlOlYphpG0n0k1SbLAppLf5EVLncsjyhaphWtpTUF8H0MYTGW90g6IBH4g0oRfU7@beforebom.postgres.svc:5432/SuffixRule_NPDM"
extraURL = "postgres://beforebom-user:vlOlYphpG0n0k1SbLAppLf5EVLncsjyhaphWtpTUF8H0MYTGW90g6IBH4g0oRfU7@beforebom-0.beforebom.postgres.svc:5432/extra"
AccMaster = "postgres://beforebom-user:vlOlYphpG0n0k1SbLAppLf5EVLncsjyhaphWtpTUF8H0MYTGW90g6IBH4g0oRfU7@beforebom-0.beforebom.postgres.svc:5432/HEROS_AccMaster"

#Pymongo
compareresult = "mongodb://resultreport-admin:a7kjzyALwazGrWxyYPJ2kUgP@resultreport-0.resultreport-svc.mongodb.svc.cluster.local:27017/admin?replicaSet=resultreport&ssl=false"
mongoURL = "mongodb://resultreport-admin:a7kjzyALwazGrWxyYPJ2kUgP@resultreport-0.resultreport-svc.mongodb.svc.cluster.local:27017/admin?replicaSet=resultreport&ssl=false"
memberURL= r"postgresql://mybini-user:vzS3Bo0K8Bx2DcHQPd0zIpkiEhjDcZKJ8vyTqHPcwF796dMbYF0m4dFaedWAxWIN@mybini-0.mybini.postgres.svc:5432/MasterMP_Data"
masterDataURL = r"postgresql://mybini-user:vzS3Bo0K8Bx2DcHQPd0zIpkiEhjDcZKJ8vyTqHPcwF796dMbYF0m4dFaedWAxWIN@mybini-0.mybini.postgres.svc:5432/MasterMP_Auto"
reportBug =r"postgresql://mybini-user:vzS3Bo0K8Bx2DcHQPd0zIpkiEhjDcZKJ8vyTqHPcwF796dMbYF0m4dFaedWAxWIN@mybini-0.mybini.postgres.svc:5432/reportBug"

#
# beview - mongo link
be_log = "mongodb://belog-admin:C2lqn5j8az1Ay14IJ254eUcD@belog-0.belog-svc.mongodb.svc.cluster.local:27017/admin?replicaSet=belog&ssl=false"
be_done = "mongodb://bedone-admin:42VIiZ8tQdpLMOGINz5ViLmF@bedone-0.bedone-svc.mongodb.svc.cluster.local:27017/admin?replicaSet=bedone&ssl=false"


def get_eax_url(soc):
    eax_url = f"postgresql://beforebom-user:vlOlYphpG0n0k1SbLAppLf5EVLncsjyhaphWtpTUF8H0MYTGW90g6IBH4g0oRfU7@beforebom-0.beforebom.postgres.svc:5432/{soc.lower()}"

    return eax_url 
