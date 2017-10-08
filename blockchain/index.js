web3 = new Web3(new Web3.providers.HttpProvider("http://localhost:8545")); 
// web3 = new Web3(new Web3.providers.HttpProvider("http://10.1.24.48:8545"));

addressVoting = '0x6c3f6de99e60f06596d94221d1593364e5a2f919';
interfaceVoting = '[{"constant":true,"inputs":[{"name":"","type":"bytes32"}],"name":"constituencyDict","outputs":[{"name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"candidate","type":"bytes32"}],"name":"totalVotesFor","outputs":[{"name":"","type":"uint8"},{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"candidate","type":"bytes32"}],"name":"getCandidateConstituency","outputs":[{"name":"","type":"bool"},{"name":"","type":"bytes32"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"candidate","type":"bytes32"}],"name":"validCandidate","outputs":[{"name":"","type":"bool"},{"name":"","type":"string"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"bytes32"}],"name":"votesReceived","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"x","type":"bytes32"}],"name":"bytes32ToString","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"uint256"}],"name":"candidateList","outputs":[{"name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"candidate","type":"bytes32"}],"name":"voteForCandidate","outputs":[{"name":"","type":"bool"},{"name":"","type":"string"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[],"name":"test","outputs":[{"name":"","type":"bool"},{"name":"","type":"string"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"inputs":[{"name":"candidateNames","type":"bytes32[]"},{"name":"constituencies","type":"bytes32[]"}],"payable":false,"stateMutability":"nonpayable","type":"constructor"}]';
abiVotingContract = JSON.parse(interfaceVoting);
VotingContract = web3.eth.contract(abiVotingContract);
votingContractInstance = VotingContract.at(addressVoting); //deep

addressAuthentication = '0xf7539535e2436889d4dedddd746461daa57f4659';
interfaceAuthentiation = '[{"constant":false,"inputs":[{"name":"candidate","type":"bytes32"},{"name":"voter","type":"bytes32"}],"name":"checkConstituency","outputs":[{"name":"","type":"bool"},{"name":"","type":"string"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"bytes32"}],"name":"constituencyDict","outputs":[{"name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"voter","type":"bytes32"}],"name":"isVoteAvailable","outputs":[{"name":"","type":"bool"},{"name":"","type":"string"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"uint256"}],"name":"voterList","outputs":[{"name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[],"name":"resetVoters","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"candidate","type":"bytes32"},{"name":"voter","type":"bytes32"}],"name":"validVoter","outputs":[{"name":"","type":"bool"},{"name":"","type":"string"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[],"name":"ping","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"bytes32"}],"name":"votesAvailable","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"x","type":"bytes32"}],"name":"bytes32ToString","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"candidate","type":"bytes32"},{"name":"voter","type":"bytes32"}],"name":"isAuthentic","outputs":[{"name":"","type":"bool"},{"name":"","type":"string"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"voter","type":"bytes32"}],"name":"isVoterExist","outputs":[{"name":"","type":"bool"},{"name":"","type":"string"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"voting","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"inputs":[{"name":"myList","type":"bytes32[]"},{"name":"constituencies","type":"bytes32[]"},{"name":"addr","type":"address"}],"payable":false,"stateMutability":"nonpayable","type":"constructor"}]';
abiAuthenticationContract = JSON.parse(interfaceAuthentiation);
AuthenticationContract = web3.eth.contract(abiAuthenticationContract);
authenticationContractInstance = AuthenticationContract.at(addressAuthentication); //deep

// In your nodejs console, execute votingContractInstance.address to get the address at which the contract is deployed and change the line below to use your deployed address
// votingContractInstance = VotingContract.at('0x2a9c1d265d06d47e8f7b00ffa987c9185aecf672'); //default
// votingContractInstance = VotingContract.at('0xd0a885aaa1255afe3f3c4695def20871d0231f72'); //my
candidates = {"Rahul Gandhi": "candidate-1", "DK Shivakumar": "candidate-2", "Ramalinga Reddy": "candidate-3", "Vijay Rupani": "candidate-4", "Arvind Kejriwal": "candidate-5", "Narendra Modi": "candidate-6"};

function voteForCandidate() {

  candidateName = $("#candidate").val();
  console.log('candidateName:' + candidateName);

  voterName = $("#voter").val();
  console.log('voterName:' + voterName);

  isAuthenticResponse = isAuthenticVoter(candidateName, voterName);
  console.log("isAuthentic:" + isAuthenticResponse);

  if(isAuthenticResponse[0] == false)
  {
    console.log(isAuthenticResponse[1]);
    alert(isAuthenticResponse[1]);
    return;
  }

  console.log("test1"+votingContractInstance.totalVotesFor.call(candidateName));
  // console.log("test2"+votingContractInstance.voteForCandidate.call(candidateName));
  votingContractInstance.voteForCandidate(candidateName, {from: web3.eth.accounts[1]}, function() {
    let div_id = candidates[candidateName];
    console.log(div_id);
    $("#" + div_id).html(votingContractInstance.totalVotesFor.call(candidateName)[0].toString());
    console.log(votingContractInstance.totalVotesFor.call(candidateName)[0].toString());
    alert("voting done");
  });
}

$(document).ready(function() {
  candidateNames = Object.keys(candidates);
  for (var i = 0; i < candidateNames.length; i++) {
    let name = candidateNames[i];
    let val = votingContractInstance.totalVotesFor.call(name)[0].toString();
    $("#" + candidates[name]).html(val);
  }
});

function isAuthenticVoter(candidateName, voterName)
{
  isAuthenticResponse = authenticationContractInstance.isAuthentic.call(candidateName, voterName);
  authenticationContractInstance.isAuthentic(candidateName, voterName, {from: web3.eth.accounts[0]}, function(){});
  return isAuthenticResponse;
}

function resetVoters()
{
  authenticationContractInstance.resetVoters({from: web3.eth.accounts[0]}, function(){});
}