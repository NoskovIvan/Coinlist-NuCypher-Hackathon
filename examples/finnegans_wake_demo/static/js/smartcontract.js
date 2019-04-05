function createContract(){
    return web3.eth.contract(abi);
}

function deployConract(){
    let contract = createContract();

    contract.new(
        {
            from: web3.eth.accounts[0],
            data: bytecode,
            gas: '4700000'
        }, function (e, contract){
            console.log(e, contract);
            if (typeof contract.address !== 'undefined') {
                console.log('Contract mined! address: ' + contract.address + ' transactionHash: ' + contract.transactionHash);
                var contract_address = contract.address;
		        console.log('Address on JS before: ' + contract.address);			
            }		  
        });
}

function openContract(address){
    let contract = createContract();
    let contractInstance = contract.at(address);
    return contractInstance;
}



function support(address) {
  web3.eth.sendTransaction({
      from: web3.eth.accounts[0],
      to: address,
      value: '1000'
  }, function(err, transactionHash) {
  if (!err)
    console.log(transactionHash); 
});
}



	


