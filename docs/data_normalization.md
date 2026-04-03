Part of the things we'll need to be aware of are the degrees of freedom for the system/satellite data. 

For individual satellites it can b:
1. 6-Directional Position
    - This would be the position of the satellite in 3D space and its orientation in 3D space. This should actually be changed to orbital parameters *(Semi-major axis, Eccentricity, Inclination, Right ascension of the ascending node, Argument of periapsis, True anomaly)* instead of cardinal directions *(Up, Down, Left, Right, Forward, Backward)*. Either way its equivalent to 6-degrees of freedom and a change in coordinate system is needed to compare them.
1. 3-Degress of Rotation
    - Degrees of rotation don't change in space since rotation is only relative to the satellite itself not to some other body. 
1. Spectral Sensitivity
    - This would be the range of wavelengths that the cameras/sensors are sensitive to. Probably the most important consideration since this will be what changes most between satellite types. Everything else can be accounted for through software but this can't.
1. Temporal Resolution
    - This would be the time it takes for the satellite to capture data. 
1. Spatial Resolution
    - This would be the resolution of the data that the satellite captures. 
1. Zoom 
    - This would be the zoom level of the satellite which would determine how much area of the earth its actually seeing. For example one sat could capture a 100km x 100km area while another could capture a 10km x 10km area. 
1. Exposure Time
    - This would be the exposure time of the satellite. 

Between different satellites we have to account for:
1. Exposure Pattern
    - Possibly different between capturing data through scanning a 1D array of pixels over time using the satellite's movement (Pushbroom) and capturing data through a 2D array of pixels at a single moment in time (Snapshot).

These differences that arise with the degress of freedom of the satellites are what make it difficult to compare data between different satellites and lead to the following problems and open questions.

**Problems:**

Some sats for exmaple only capture in specific bands of light, others capture in a wide range of bands.

1. **Non-Intersecting Band Problem**

    Say Sat. 1 has three bands that are only sensitive to Red in 650-700nm, Green in 500-550nm, and Blue in 450-500nm but Sat. 2 has 3 bands at 650-600nm, 450-500nm, and 400-450nm. How are we going to compare them? Especially since in this case they have no overlap in sensitivity. 

    *Open Questions:*
    
    - Can we only do comparisons betweeen images of the same band type (ie: when they are sensitive to the same wavelengths of light)? 
        - This would result in only being able to compare results of sats. from the same consellation or manufacturer since there is no standard for spectral sensitivity between different satellite manufacturers. 
    - Is there possibly some standardization between satellite manufactures that I am not aware of? Or a series of bands that are common to most satellites that we can use as a baseline for comparison? (eg: Red is defined as 650nm always, Green is defined as 550nm always, etc.)

2. **Subset Band Problem**

    Say Sat. 1 has sentivity to bands 750-720nm, 650-620nm, 550-520nm and Sat. 2 has senitivity to bands 740-730nm, 640-630nm, 540-530nm. How do a comparison between a subset and superset of spectral data?

    *Open Questions:*

    - If we have 1 satellites bands as a subset of anothers can we make the comparison? To what degree of accuracy can we do this?

3. **Certainty Problem**

    *Open Questions:*

    - How do we calculate general degree of certainty between any artbirary comparison?

4. **Interband Relationship Problem**

    *Open Questions:*

    - Can we validate the data of hyperspectral bands of one image? (eg: Sat. 1 has 12 bands, can we use band 1 and 3 to validate the data of band 2?)


Naive Mathematical Formulation

Lets try to create a rudimentary mathematical formulation of the problem. Specifically for what the difference of bands means.

For a semi-realistic treatment lets take the difference between two 3-dimensional matrices representing the full range of bands given by two different satellites. 

Say Sat A has 3 bands/images of size n by m and Sat B has 3 bands/images of size p by q where n is not neccessarily equal to p and m is not neccessarily equal to q and n,m,p,q are all postive integers.

Then each of the bands can be represented by a matrix of size n by m and p by q respectively. The set of bands $\bar{A} = \{A_1, A_2, \dots, A_a\}$ and $\bar{B} = \{B_1, B_2, \dots, B_b\}$ where $A_i$ and $B_i$ are matrices of size n by m and p by q respectively and $\bar{A}$ are of dimesionality $a \times n \times m$ and $\bar{B}$ are of dimensionality $b \times p \times q$.
