// SPDX-License-Identifier: MIT
pragma solidity >=0.4.22 <0.9.0;

contract crowdfunding {

  string[] _usernames;
  string[] _emails;
  string[] _passwords;

  string[] _orgnames;
  string[] _orgyears;
  string[] _orgcontacts;
  string[] _orgaddress;
  string[] _orgpasswords;
  uint[] _orgids;
  uint[] _orgstatus;

  string[] _rpurpose;
  uint[] _ramount;
  string[] _rusernames;
  uint[] _rids;
  uint[] _rstatus;
  uint[] _rdonations;

  uint[] _rgids;
  uint[] _gids;
  string[] _gusernames;
  uint[] _gdonations;

  string[] _uusernames;
  string[] _upurposes;
  uint[] _uamounts;
  string[] _ufiles;
  uint[] _reqids;

  mapping(string=>bool) _registeredusers;
  mapping(string=>bool) _registeredemails;
  mapping(string=>bool) _registeredorgs;
  mapping(string=>bool) _registeredinvoices;

  uint orgid;
  uint rid;
  uint gid;
  address admin;
  string adminp="1234";

  constructor() {
    orgid=0;
    rid=0;
    gid=0;
    admin=msg.sender;
  }

  function signup(string memory username,string memory email,string memory password) public {
    require(!_registeredusers[username]);
    require(!_registeredemails[email]);

    _usernames.push(username);
    _emails.push(email);
    _passwords.push(password);
    
    _registeredusers[username]=true;
    _registeredemails[email]=true;
  }

  function viewusers() public view returns(string[] memory,string[] memory,string[] memory){
    return(_usernames,_emails,_passwords);
  }

  function addOrganisation(string memory orgname,string memory orgyear,string memory orgcontact,string memory orgadd,string memory orgpass) public {
    require(!_registeredorgs[orgcontact]);

    orgid+=1;
    _orgnames.push(orgname);
    _orgyears.push(orgyear);
    _orgcontacts.push(orgcontact);
    _orgaddress.push(orgadd);
    _orgpasswords.push(orgpass);
    _orgstatus.push(0);
    _orgids.push(orgid);

    _registeredorgs[orgcontact]=true;
  }

  function viewOrganisations() public view returns(string[] memory,string[] memory,string[] memory,string[] memory,string[] memory,uint[] memory,uint[] memory){
    return(_orgnames,_orgyears,_orgcontacts,_orgaddress,_orgpasswords,_orgstatus,_orgids);
  }

  function viewAdmin() public view returns(address,string memory) {
    return(admin,adminp);
  }

  function updateOrg(uint orgid1,uint status) public{
    uint i;

    for(i=0;i<_orgids.length;i++){
      if(orgid1==_orgids[i]){
        _orgstatus[i]=status;
      }
    }
  }

  function addRequest(string memory purpose,uint amount,string memory username) public {
    rid+=1;
    _rpurpose.push(purpose);
    _ramount.push(amount);
    _rusernames.push(username);
    _rids.push(rid);
    _rstatus.push(0);
    _rdonations.push(0);
  }

  function viewRequests() public view returns(string[] memory,uint[] memory,string[] memory,uint[] memory,uint[] memory,uint[] memory){
    return (_rpurpose,_ramount,_rusernames,_rids,_rstatus,_rdonations);
  }

  function addDonation(uint amount,uint reqid,string memory username) public {
    uint i;

    gid+=1;
    _rgids.push(reqid);
    _gids.push(gid);
    _gusernames.push(username);
    _gdonations.push(amount);

    for(i=0;i<_rids.length;i++){
      if(_rids[i]==reqid){
        _rdonations[i]+=amount;
        if(_rdonations[i]==_ramount[i]){
          _rstatus[i]=1;
        }
      }
    }
  }

  function viewDonations() public view returns(uint[] memory,uint[] memory,string[] memory,uint[] memory) {
    return(_rgids,_gids,_gusernames,_gdonations);
  } 

  function updateRequest(uint rid1,uint status) public{
    uint i;

    for(i=0;i<_rids.length;i++){
      if(_rids[i]==rid1){
        _rstatus[i]=status;
      }
    }
  }

  function addUtilisation(string memory username,string memory purpose,uint amount, string memory invoice,uint reqid) public {

    require(!_registeredinvoices[invoice]);
    _uusernames.push(username);
    _upurposes.push(purpose);
    _uamounts.push(amount);
    _ufiles.push(invoice);
    _reqids.push(reqid);

    _registeredinvoices[invoice]=true;

  }

  function viewUtilisations() public view returns(string[] memory,uint[] memory, string[] memory,string[] memory,uint[] memory){
    return(_upurposes,_uamounts,_ufiles,_uusernames,_reqids);
  }

}
