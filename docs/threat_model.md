Goal: Define what we are protecting against and from whom.

Key Questions: 
- Trust Assumptions: Do nodes need to trust each other?
- Adversarial Model: What can a malicous actor do? (e.g. Sybil attacks, eclipse attacks, man-in-the-middle attacks, etc.)
- Mitigation Strategies: How do we mitigate these threats?

## Threat Mitigation (from Whitepaper v0.3)

By being critical of the data our network participants exchange we can better adapt Iris to handle malicious actors, their attacks and any inaccurate information. The Average Scenario of a location is therefore the best estimate we have for an image of the AoI requested.


### Problems

Need a tamper-proof way to prove that the image came from the satellite provider.

Need a tamper-proof way of assigning land ownership.
- Endogenous Solution #1 (Feature-Based Verification): We can use the network (Iris) to recognize owner-made terrestrial features. This could be something like writing a specific code or word that is only given to the requesting user/owner. Similar to the concept of writing your name OR "SOS" in the sand, but with a code that is only visible from space. 
   - Problems: This would be difficult if not neglegent to have as a system for users whose lands are heavily forested or otherwise covered by natural features that would obscure the code. This includes small areas that might not have the same required for the code to be visible. Nor would it work for land that is protected legally or cannot sustain further modification. 

- Exogenous Solution #1 (Mobile Device Verification): Use a cellphone or simialr geospatially aware device to ping the edges or walk continuously through the property boundaries to prove ownership. Having the user verify the boundaries of their land using either point or continous line data based on geographical information wouldn't neccesarily prove that they are the owner but it would prove that they have access to the land and can traverse it.
   - Problems: 
      - Geospatial information can be spoofed.
      - Mobile or consumer grade devices with Geospatial capabilities are not always accurate.
      - Someone could trace the land owner's property from the outside and no actually have access to the land.

- Exogenous Solution #2 (Custom Hardware): Use of bespoke/custom hardware that is in constant communication with the internet using something like starlink. Could be a part of an extension to the Iris network or a separate network entirely. Fundamentally it is a different verification architecture and would have to be passed down from a 3rd-party, in this case the manufacturer of the hardware, to the user.
   - Problems: 
      - Expensive to produce and distribute.
      - Expensive to buy.
      - Doesnt have the averaging benefit from multiple data sources instead it only relies on one.
      - Custom hardware can be tampered with and with enough resources could be spoofed.

- Exogenous Solution #3 (Ground-based Landmark Imagery): The Iris network can request the user looking for ownership of property verification take multiple randomly designated pictures of features visible from space. The images would then have to be cross-referenced with the satellite imagery to verify the user's ownership.      
   - Problems: 
      - We would have to extend the Iris network to include nodes that can take pictures of the ground. 
      - Single source of truth for the ground-based imagery. 
      - If the area is small enough the imagery can be taken from outside the bounds of the property.
      - If the area is large enough, and the land is not densely populated or has limited resources, it would allow bad actors to come in and take pictures of the landmarks to spoof the system. 

### Penalty Mechanism

   1. The Regular Nodes that provided images close to the Average Scenario are more likely to be honest because they were close to the majority of all other images. Therefore the smart contract rewards the regular nodes.
   2. The Regular Nodes whose images are statistically dissimilar to the Average Scenario have their stakes tokens burnt as punishment. Again the smart contract executes the penalty.
