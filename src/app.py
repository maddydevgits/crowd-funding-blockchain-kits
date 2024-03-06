from flask import Flask,render_template,request,session,redirect
from web3 import Web3,HTTPProvider
import json
from werkzeug.utils import secure_filename
import ipfsapi
import os

app=Flask(__name__)
app.secret_key='5000'
app.config['uploads']="uploads"

def connect_with_blockchain(acc):
    web3=Web3(HTTPProvider('http://127.0.0.1:7545'))
    
    if acc==0:
        web3.eth.defaultAccount=web3.eth.accounts[0]
    else:
        web3.eth.defaultAccount=acc
    
    artifact_path="./build/contracts/crowdfunding.json"
    with open(artifact_path) as f:
        artifact_json=json.load(f)
        contract_abi=artifact_json['abi']
        contract_address=artifact_json['networks']['5777']['address']
    
    contract=web3.eth.contract(abi=contract_abi,address=contract_address)
    return contract,web3
    

@app.route('/')
def land():
    return render_template('land.html')

@app.route('/log')
def log():
    return render_template('login.html')

@app.route('/reg')
def reg():
    return render_template('register.html')

@app.route('/register',methods=['post','get'])
def register():
    username=request.form['username']
    email=request.form['email']
    password=request.form['password']
    confirmpass=request.form['cpassword']
    if password!=confirmpass:
        return render_template('register.html',status='passwords didnt matched')
    else:
        try:
            contract,web3=connect_with_blockchain(0)
            tx_hash=contract.functions.signup(username,email,password).transact()
            web3.eth.waitForTransactionReceipt(tx_hash)
            return render_template('register.html',stat="Registration successful")
        except:
            return render_template('register.html',status='signup failed')


@app.route('/login',methods=['post','get'])
def login():
    user=request.form['username']
    password=request.form['password']
    contract,web3=connect_with_blockchain(0)
    _usernames,_emails,_passwords=contract.functions.viewusers().call()

    for i in range(len(_usernames)):
        if _usernames[i]==user and _passwords[i]==password:
            session['username']=user
            session['type']=1
            return render_template('index.html')
    return render_template('login.html',status='login invalid')

@app.route('/orgsignup')
def orgsignup():
    return render_template('organisationregister.html')

@app.route('/organisationregisterform',methods=['post'])
def organisationregisterform():
    name=request.form['name']
    year=request.form['year']
    contact=request.form['contact']
    address=request.form['address']
    password=request.form['password']
    print(name,year,contact,address,password)
    try:
        contract,web3=connect_with_blockchain(0)
        tx_hash=contract.functions.addOrganisation(name,year,contact,address,password).transact()
        web3.eth.waitForTransactionReceipt(tx_hash)
        return render_template('organisationregister.html',stat='request sent')
    except:
        return render_template('organisationregister.html',status='request already sent')

@app.route('/adlog',methods=['post'])
def adlog1():
    username=request.form['username']
    password=request.form['password']
    contract,web3=connect_with_blockchain(0)
    admin,adminp=contract.functions.viewAdmin().call()
    if admin==username and password==adminp:
        return redirect('/orgverification')
    else:
        return render_template('adminlogin.html',status='admin invalid')

@app.route('/orgverification')
def orgverification():
    contract,web3=connect_with_blockchain(0)
    _orgnames,_orgyears,_orgcontacts,_orgaddress,_orgpasswords,_orgstatus,_orgids=contract.functions.viewOrganisations().call()
    data=[]
    for i in range(len(_orgnames)):
        dummy=[]
        if(_orgstatus[i]==0):
            dummy.append(_orgnames[i])
            dummy.append(_orgyears[i])
            dummy.append(_orgcontacts[i])
            dummy.append(_orgaddress[i])
            dummy.append(_orgpasswords[i])
            dummy.append(_orgstatus[i])
            dummy.append(_orgids[i])
            data.append(dummy)
    return render_template('orgverification.html',l=len(data),dashboard_data=data)

@app.route('/acceptorg/<id1>/<id2>')
def acceptorg(id1,id2):
    print(id1,id2)
    contract,web3=connect_with_blockchain(0)
    tx_hash=contract.functions.updateOrg(int(id1),int(id2)).transact()
    web3.eth.waitForTransactionReceipt(tx_hash)
    return redirect('/orgverification')

@app.route('/denyorg/<id1>/<id2>')
def denyorg(id1,id2):
    print(id1,id2)
    contract,web3=connect_with_blockchain(0)
    tx_hash=contract.functions.updateOrg(int(id1),int(id2)).transact()
    web3.eth.waitForTransactionReceipt(tx_hash)
    return redirect('/orgverification')

@app.route('/approvedorgs')
def approvedorgs():
    contract,web3=connect_with_blockchain(0)
    _orgnames,_orgyears,_orgcontacts,_orgaddress,_orgpasswords,_orgstatus,_orgids=contract.functions.viewOrganisations().call()
    data=[]
    for i in range(len(_orgnames)):
        dummy=[]
        if(_orgstatus[i]==1):
            dummy.append(_orgnames[i])
            dummy.append(_orgyears[i])
            dummy.append(_orgcontacts[i])
            dummy.append(_orgaddress[i])
            dummy.append(_orgpasswords[i])
            dummy.append(_orgstatus[i])
            dummy.append(_orgids[i])
            data.append(dummy)
    return render_template('approvedorgs.html',l=len(data),dashboard_data=data)

@app.route('/deniedorgs')
def deniedorgs():
    contract,web3=connect_with_blockchain(0)
    _orgnames,_orgyears,_orgcontacts,_orgaddress,_orgpasswords,_orgstatus,_orgids=contract.functions.viewOrganisations().call()
    data=[]
    for i in range(len(_orgnames)):
        dummy=[]
        if(_orgstatus[i]==2):
            dummy.append(_orgnames[i])
            dummy.append(_orgyears[i])
            dummy.append(_orgcontacts[i])
            dummy.append(_orgaddress[i])
            dummy.append(_orgpasswords[i])
            dummy.append(_orgstatus[i])
            dummy.append(_orgids[i])
            data.append(dummy)
    return render_template('approvedorgs.html',l=len(data),dashboard_data=data)

@app.route('/orgloginform',methods=['post'])
def orgloginform():
    username=request.form['username']
    password=request.form['password']
    contract,web3=connect_with_blockchain(0)
    _orgnames,_orgyears,_orgcontacts,_orgaddress,_orgpasswords,_orgstatus,_orgids=contract.functions.viewOrganisations().call()
    for i in range(len(_orgnames)):
        if username==_orgcontacts[i]:
            if _orgstatus[i]==0:
                return render_template('organisationlogin.html',status='you are on hold')
            elif _orgstatus[i]==2:
                return render_template('organisationlogin.html',status='you are denied')
            else:
                if password==_orgpasswords[i]:
                    session['username']=username
                    session['type']=2
                    return render_template('organisationindex.html')
                else:
                    return render_template('organisationlogin.html',status='invalid login')
    return render_template('organisationlogin.html',status='no account with this username')

@app.route('/organisationrequestform',methods=['post','get'])
def organisationrequestform():
    purpose=request.form['purpose']
    amount=request.form['amount']
    username=session['username']
    contract,web3=connect_with_blockchain(0)
    tx_hash=contract.functions.addRequest(purpose,int(amount),username).transact()
    web3.eth.waitForTransactionReceipt(tx_hash)
    return render_template('organisationrequest.html',status='request sent')

@app.route('/orglogin')
def orglogin():
    return render_template('organisationlogin.html')

@app.route('/organisationhome')
def organisationhome():
    return render_template('organisationindex.html')

@app.route('/orgrequest')
def organisationrequest():
    return render_template('organisationrequest.html')

@app.route('/orgrequests')
def orgrequests():
    data=[]
    contract,web3=connect_with_blockchain(0)
    _rpurpose,_ramount,_rusernames,_rids,_rstatus,_rdonations=contract.functions.viewRequests().call()
    for i in range(len(_rpurpose)):
        if _rusernames[i]==session['username']:
            dummy=[]
            dummy.append(_rpurpose[i])
            dummy.append(_ramount[i])
            dummy.append(_rids[i])
            if(_rstatus[i]==0):
                dummy.append('Open')
            else:
                dummy.append('Close')
            data.append(dummy)
    return render_template('orgrequests.html',l=len(data),dashboard_data=data)

@app.route('/allrequests')
def allrequests():
    contract,web3=connect_with_blockchain(0)
    _rpurpose,_ramount,_rusernames,_rids,_rstatus,_rdonations=contract.functions.viewRequests().call()
    data=[]
    for i in range(len(_rpurpose)):
        if(_rstatus[i]==0):
            dummy=[]
            dummy.append(_rpurpose[i])
            dummy.append(_ramount[i])
            _orgnames,_orgyears,_orgcontacts,_orgaddress,_orgpasswords,_orgstatus,_orgids=contract.functions.viewOrganisations().call()
            oindex=_orgcontacts.index(_rusernames[i])
            oname=_orgnames[oindex]
            dummy.append(_rusernames[i])
            dummy.append(oname)
            dummy.append(_rids[i])
            dummy.append(_rdonations[i])
            data.append(dummy)        

    return render_template('allrequests.html',dashboard_data=data,l=len(data))

@app.route('/donateamount/<id>')
def donateamount(id):
    session['id']=int(id)
    return render_template('contributeamount.html')

@app.route('/contribute',methods=['post'])
def contribute():
    amount=int(request.form['amount'])
    id=int(session['id'])
    username=session['username']
    contract,web3=connect_with_blockchain(0)
    _rpurpose,_ramount,_rusernames,_rids,_rstatus,_rdonations=contract.functions.viewRequests().call()
    for i in range(len(_rids)):
        if _rids[i]==id:
            if _rstatus[i]==0:
                if int(_ramount[i])-_rdonations[i]>=amount:
                    tx_hash=contract.functions.addDonation(amount,id,username).transact()
                    web3.eth.waitForTransactionReceipt(tx_hash)
                    return render_template('contributeamount.html',status='donation accepted')
                else:
                    return render_template('contributeamount.html',status='donation exceeded')
            else:
                return render_template('contributeamount.html',status='donation closed')

@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/ahome')
def ahome():
    return render_template('land.html')

@app.route('/myrequests')
def myrequests():
    return render_template('myrequests.html')

@app.route('/mydonations')
def mydonations():
    contract,web3=connect_with_blockchain(0)
    _rgids,_gids,_gusernames,_gdonations=contract.functions.viewDonations().call()
    _rpurpose,_ramount,_rusernames,_rids,_rstatus,_rdonations=contract.functions.viewRequests().call()
    data=[]
    for i in range(len(_rgids)):
        if session['username']==_gusernames[i]:
            dummy=[]
            dummy.append(_rgids[i])
            dummy.append(_gids[i])
            r1index=_rids.index(_rgids[i])
            dummy.append(_rpurpose[r1index])
            rindex=_rids.index(_rgids[i])
            rusername=_rusernames[rindex]
            _orgnames,_orgyears,_orgcontacts,_orgaddress,_orgpasswords,_orgstatus,_orgids=contract.functions.viewOrganisations().call()
            oindex=_orgcontacts.index(rusername)
            dummy.append(_orgnames[oindex])
            dummy.append(_gdonations[i])
            data.append(dummy)
    return render_template('userdonations.html',l=len(data),dashboard_data=data)

@app.route('/mycontributors')
def mycontributors():
    data=[]
    contract,web3=connect_with_blockchain(0)
    _rgids,_gids,_gusernames,_gdonations=contract.functions.viewDonations().call()
    _rpurpose,_ramount,_rusernames,_rids,_rstatus,_rdonations=contract.functions.viewRequests().call()
    data=[]
    for i in range(len(_rgids)):
        rindex=_rids.index(_rgids[i])
        rusername=_rusernames[rindex]
        if rusername==session['username']:
            dummy=[]
            dummy.append(_rgids[i])
            dummy.append(_gids[i])
            dummy.append(_gusernames[i])
            _usernames,_emails,_passwords=contract.functions.viewusers().call()
            userindex=_usernames.index(_gusernames[i])
            dummy.append(_emails[userindex])
            r1index=_rids.index(_rgids[i])
            dummy.append(_rpurpose[r1index])
            rindex=_rids.index(_rgids[i])
            rusername=_rusernames[rindex]
            _orgnames,_orgyears,_orgcontacts,_orgaddress,_orgpasswords,_orgstatus,_orgids=contract.functions.viewOrganisations().call()
            oindex=_orgcontacts.index(rusername)
            dummy.append(_orgnames[oindex])
            dummy.append(_gdonations[i])
            data.append(dummy)

    return render_template('mycontributors.html',l=len(data),dashboard_data=data)

@app.route('/donations')
def donations():
    return render_template('donations.html')

@app.route('/donate',methods=['get','post'])
def donate():
    name=request.form['name']
    phone=request.form['phone']
    don=request.form['donation']
    address=request.form['address']
    message=request.form['text']
    return render_template('index.html',status="Thanks for your donation.Our team will collect the donations ASAP")

@app.route('/donationqueue')
def donationqueue():
    return render_template('donationqueue.html')

@app.route('/dist')
def distr():
    return render_template('distribute.html')

@app.route('/distribute',methods=['get','post'])
def dist():
    name=request.args['name']
    phone=request.args['phone']
    don=request.args['donation']
    address=request.args['address']
    id=request.args['id']
    return render_template('distribute.html',stat="Distribution successful")

@app.route('/admin')
def admi():
    return render_template('adminlogin.html')

@app.route('/adindex')
def adindex():
    return render_template('adminindex.html')

@app.route('/logout')
def logout():
    session['name']=''
    return render_template('land.html')

@app.route('/uindex')
def uindex():
    return render_template('index.html')

@app.route('/alogout')
def logou():
    return render_template('land.html')

@app.route('/request',methods=['get','post'])
def req():
    name=request.form['name']
    phone=request.form['phone']
    don=request.form['donation']
    address=request.form['address']
    message=request.form['text']
    return render_template('index.html',status="Your request has been submitted successfully")

@app.route('/showrequests')
def showrequests():
    return render_template('requests.html')

@app.route('/userdonations')
def userdon():
    return render_template('/userdonations.html')

@app.route('/adminhome')
def adminhome():
    return render_template('adminindex.html')

@app.route('/admindonations')
def admindonations():
    return render_template('admindonations.html')

@app.route('/utilizations')
def utilizations():
    contract,web3=connect_with_blockchain(0)
    _rpurpose,_ramount,_rusernames,_rids,_rstatus,_rdonations=contract.functions.viewRequests().call()
    data=[]
    for i in range(len(_rpurpose)):
        if _rusernames[i]==session['username']:
            dummy=[]
            dummy.append(_rids[i])
            dummy.append(_rpurpose[i])
            data.append(dummy)
    return render_template('utilizations.html',l1=len(data),dashboard_data=data)

@app.route('/distribution',methods=['post'])
def distribution():
    reqid=int(request.form['reqid'])
    purpose=request.form['purpose']
    amount=request.form['amount']
    chooseFile=request.files['chooseFile']
    doc=secure_filename(chooseFile.filename)
    chooseFile.save('src/'+app.config['uploads']+'/'+doc)
    client=ipfsapi.Client('127.0.0.1',5001)
    print('src/'+app.config['uploads']+'/'+doc)
    response=client.add('src/'+app.config['uploads']+'/'+doc)
    print(response)
    filehash=response['Hash']
    print(filehash)
    try:
        contract,web3=connect_with_blockchain(0)
        tx_hash=contract.functions.addUtilisation(session['username'],purpose,int(amount),filehash,reqid).transact()
        web3.eth.waitForTransactionReceipt(tx_hash)
        contract,web3=connect_with_blockchain(0)
        _rpurpose,_ramount,_rusernames,_rids,_rstatus,_rdonations=contract.functions.viewRequests().call()
        data=[]
        for i in range(len(_rpurpose)):
            if _rusernames[i]==session['username']:
                dummy=[]
                dummy.append(_rids[i])
                dummy.append(_rpurpose[i])
                data.append(dummy)
        return render_template('utilizations.html',status='utilization updated',l1=len(data),dashboard_data=data)
    except:
        contract,web3=connect_with_blockchain(0)
        _rpurpose,_ramount,_rusernames,_rids,_rstatus,_rdonations=contract.functions.viewRequests().call()
        data=[]
        for i in range(len(_rpurpose)):
            if _rusernames[i]==session['username']:
                dummy=[]
                dummy.append(_rids[i])
                dummy.append(_rpurpose[i])
                data.append(dummy)
        return render_template('utilizations.html',status='already uploaded',l1=len(data),dashboard_data=data)

@app.route('/myutilizations')
def myutilizations():
    contract,web3=connect_with_blockchain(0)
    _upurposes,_uamounts,_ufiles,_uusernames,_reqids=contract.functions.viewUtilisations().call()
    data=[]
    for i in range(len(_upurposes)):
        if(_uusernames[i]==session['username']):
            dummy=[]
            dummy.append(_upurposes[i])
            dummy.append(_uamounts[i])
            dummy.append(_ufiles[i])
            dummy.append(_reqids[i])
            data.append(dummy)
    return render_template('myutilizations.html',l=len(data),dashboard_data=data)

@app.route('/myutilisations')
def myutilisations():
    contract,web3=connect_with_blockchain(0)
    _rgids,_gids,_gusernames,_gdonations=contract.functions.viewDonations().call()
    _upurposes,_uamounts,_ufiles,_uusernames,_reqids=contract.functions.viewUtilisations().call()
    data=[]
    reqids=[]
    for i in range(len(_gusernames)):
        if _rgids[i] not in reqids:
            reqids.append(_rgids[i])
    for i in range(len(_upurposes)):
        if _reqids[i] in reqids:
            dummy=[]
            dummy.append(_upurposes[i])
            dummy.append(_uamounts[i])
            dummy.append(_ufiles[i])
            dummy.append(_uusernames[i])
            data.append(dummy)
    return render_template('myutilisations.html',l=len(data),dashboard_data=data)        

if __name__=="__main__":
    app.run(debug=True)