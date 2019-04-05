pragma solidity ^0.4.0;

contract owned {

    address public owner;
   

    function owned() payable {
        owner = msg.sender;
    }
    
    modifier onlyOwner {
        require(owner == msg.sender);
        _;
    }

    function changeOwner(address _owner) onlyOwner public {
        owner = _owner;
    }
}

contract Crowdsale is owned {
    
    uint256 public totalSupply;
    string public name;
    string public media_name;
    mapping (address => uint256) public balanceOf;

    event Transfer(address indexed from, address indexed to, uint256 value);

    function Crowdsale() payable owned() {
        totalSupply = 1200;
        name="J.K.Rowling";
        media_name="Harry Potter and encrypted message";
        balanceOf[this] = 1000;
        balanceOf[owner] = totalSupply - balanceOf[this];
        Transfer(this, owner, balanceOf[owner]);
    }

    function () payable {
        require(balanceOf[this] > 0);
        uint256 tokensPerOneEther = 1000;
        uint256 tokens = tokensPerOneEther * msg.value / 1000000000000000000;
        if (tokens > balanceOf[this]) {
            tokens = balanceOf[this];
            uint valueWei = tokens * 1000000000000000000 / tokensPerOneEther;
            msg.sender.transfer(msg.value - valueWei);
        }
        require(tokens > 0);
        balanceOf[msg.sender] += tokens;
        balanceOf[this] -= tokens;
        Transfer(this, msg.sender, tokens);
    }
    
    function SetMediaInfo(string _name, string _media_name) public {
        name = _name;
        media_name = _media_name;
    }
    
    function GetName() public view returns (string) {
        return(name);
    }
    
    function GetMediaName() public view returns (string) {
        return(media_name);
    }
    
}

contract EasyToken is Crowdsale {
    
    string  public standard    = 'Token 0.1';
    string  public name        = 'EasyTokenr';
    string  public symbol      = "ETT";
    uint8   public decimals    = 0;
    

    function EasyToken() payable Crowdsale() {}

    function transfer(address _to, uint256 _value) public {
        require(balanceOf[msg.sender] >= _value);
        balanceOf[msg.sender] -= _value;
        balanceOf[_to] += _value;
        Transfer(msg.sender, _to, _value);
    }
}

contract EasyCrowdsale is EasyToken {

    function EasyCrowdsale() payable EasyToken() {}
    
    function withdraw() public onlyOwner {
        owner.transfer(this.balance);
    }
    
    function killMe() public onlyOwner {
        selfdestruct(owner);
    }
}
