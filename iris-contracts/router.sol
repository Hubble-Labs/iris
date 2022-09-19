// SPDX-License-Identifier: MIT
pragma solidity ^0.8.7;

import "@chainlink/contracts/src/v0.8/interfaces/VRFCoordinatorV2Interface.sol";
import "@chainlink/contracts/src/v0.8/VRFConsumerBaseV2.sol";


contract VRFv2Consumer is VRFConsumerBaseV2 {
  VRFCoordinatorV2Interface COORDINATOR;

    event FulfilledVar(uint256 requestId, uint256 value, address leader);
  // Your subscription ID.
  uint64 s_subscriptionId;

  // Goerli coordinator. For other networks,
  // see https://docs.chain.link/docs/vrf-contracts/#configurations
  //0x2Ca8E0C643bDe4C2E08ab1fA0da3401AdAD7734D
  address s_vrfCoordinator;

  // The gas lane to use, which specifies the maximum gas price to bump to.
  // For a list of available gas lanes on each network,
  // see https://docs.chain.link/docs/vrf-contracts/#configurations
  // 0x79d3d8832d904592c0bf9818b621522c988bb8b0c05cdc3b15aea1b6e8db0c15
  bytes32 s_keyHash;

  // Depends on the number of requested values that you want sent to the
  // fulfillRandomWords() function. Storing each word costs about 20,000 gas,
  // so 100,000 is a safe default for this example contract. Test and adjust
  // this limit based on the network that you select, the size of the request,
  // and the processing of the callback request in the fulfillRandomWords()
  // function.
  uint32 callbackGasLimit = 50000;

  // The default is 3, but you can set this higher.
  uint16 requestConfirmations = 3;

  // For this example, retrieve 1 random values in one request.
  // Cannot exceed VRFCoordinatorV2.MAX_NUM_WORDS.
  uint32 numWords =  1;

  uint256 public s_randomWords;
  uint256 public s_requestId;
  address s_owner;

  address public leader_node;

  address s_oracleA;
  address s_oracleB;
  address s_oracleC;



  constructor(uint64 subscriptionId, address vrfCoordinator, bytes32 keyHash, address oracleA, address oracleB, address oracleC) VRFConsumerBaseV2(vrfCoordinator) {
    COORDINATOR = VRFCoordinatorV2Interface(vrfCoordinator);
    s_owner = msg.sender;
    s_subscriptionId = subscriptionId;
    s_keyHash = keyHash;
    s_oracleA = oracleA;
    s_oracleB = oracleB;
    s_oracleC = oracleC;
  }


  function updateVariable() public {
    s_requestId = COORDINATOR.requestRandomWords(
        s_keyHash,
        s_subscriptionId,
        requestConfirmations,
        callbackGasLimit,
        numWords
    );
    
  }

    function fulfillRandomWords(uint256 requestId, uint256[] memory randomWords) internal override {
        s_randomWords = (randomWords[0] % 3) + 1;
        if (s_randomWords % 2 == 0) {
            leader_node = s_oracleA;
        } else if (s_randomWords % 3 == 0) {
            leader_node = s_oracleB;
        } else {
            leader_node = s_oracleC;
        fulfillVar(requestId, s_randomWords);
    }
}

    function fulfillVar(uint256 requestId, uint256 randomWord) private {
        // execution path A
        emit FulfilledVar(requestId, randomWord, leader_node);
    }


  modifier onlyOwner() {
    require(msg.sender == s_owner);
    _;
  }
}

