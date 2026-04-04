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

Lets start by stating the problem in specific context then move to the general formulation.

### Simplest Example:
<!--- I want to formulate this point as a physics problem in english then put all the defintions in the bottom before I get to the math. 
--->

We first want to start with the simplest forumation with the following assumptions:
1. The images of Sat. A and Sat. B are the same size and resolution.
2. The bands of Sat. A and Sat. B are the same.
3. The uncertainty of the data is not a factor.
4. The images were taken at differnt times but of the same location from the same satellite.

Say Sat. A has $3$ bands/images of size $1024 \times 1024$ pixels and Sat. B has $3$ bands/images of size $1024 \times 1024$ pixels.

Then the difference between the two satellites is the difference between the two matrices with the Hamming distance as the metric. 

Suppose we call Sat. A's bands $A_1, A_2, A_3$ and Sat. B's bands $B_1, B_2, B_3$. With the set of these matrices being $\bar{A}$ and $\bar{B}$ respectively. That way $A_i$ and $B_i$ are the ith element of the set of matrices. 

#### Defintions:
- Sat. A has $a=3$ bands/images of size $N \times M$ such that:
    - $a$ = number of bands/images, where $a \in \mathbb{Z}^+$
    - $N$ = number of rows, where $N \in \mathbb{Z}^+$
    - $M$ = number of columns, where $M \in \mathbb{Z}^+$
    - $A_i$ = the i-th band/image, where $A_i$ is a matrix of size $N \times M$
    - $\bar{A}$ = the set of all bands/images, where $\bar{A}$ is a matrix of size $a \times N \times M$
- Sat. B has $b = 3$ bands/images of size $P \times Q$ such that:
    - $b$ = number of bands/images, where $b \in \mathbb{Z}^+$
    - $P$ = number of rows, where $P \in \mathbb{Z}^+$
    - $Q$ = number of columns, where $Q \in \mathbb{Z}^+$
    - $B_i$ = the i-th band/image, where $B_i$ is a matrix of size $P \times Q$
    - $\bar{B}$ = the set of all bands/images, where $\bar{B}$ is a matrix of size $b \times P \times Q$
- The transfer function from the full range of wavelengths to the bands/images is defined as $C$ for Camera. It takes in the full range of wavelengths possible over essentially infinite resolution and outputs the bands/images finite $N \times M$ resolution.
    - $C: {\mathbb{R}^{3+}} \to \mathbb{R_{0 \to 1}}^a \times \mathbb{Z}^{N+} \times \mathbb{Z}^{M+}$
- Let $\lambda = \{0 \dots \infty\}$ be the full range of wavelengths. Then $\lambda_C = \{min(C), \dots, max(C)\}$ is the range of wavelengths that the camera/sensor is sensitive to. Finally $\bar{\lambda}_C = \{\lambda_1, \dots, \lambda_a\}$ is the set of the average wavelengths that the sensor can detect.
    - $\lambda = \{0 \dots \infty\}$
    - $\lambda_C = \{min(C), \dots, max(C)\}$ (should change the variable name to something other than C since its not the function or set of possible function values but the range of wavelengths that the camera/sensor is sensitive to)
    - $\bar{\lambda}_C = \{\lambda_1, \dots, \lambda_a\}$


Then each of the bands can be represented by a matrix of size n by m and p by q respectively. The set of bands $\bar{A} = \{A_1, A_2, \dots, A_a\}$ and $\bar{B} = \{B_1, B_2, \dots, B_b\}$ where $A_i$ and $B_i$ are matrices of size n by m and p by q respectively and $\bar{A}$ are of dimesionality $a \times n \times m$ and $\bar{B}$ are of dimensionality $b \times p \times q$.

The field that S is, is yet to be determined but im thinking it has to be a modulo field since the individual values are going to be interpreted as grey scale or intensity at specific wavelengths. Therefore I believe it has to be a field of real numbers between 0 and 1 modulo 1. As far as I recall we need a field in order to make use of vector spaces.

#### General:

- Sat. A has $a=3$ bands/images of size $N \times M$ such that:
    - $a$ = number of bands/images, where $a \in \mathbb{Z}^+$
    - $N$ = number of rows, where $N \in \mathbb{Z}^+$
    - $M$ = number of columns, where $M \in \mathbb{Z}^+$
    - $A_i$ = the i-th band/image, where $A_i$ is a matrix of size $N \times M$
    - $\bar{A}$ = the set of all bands/images, where $\bar{A}$ is a matrix of size $a \times N \times M$
- Sat. B has $b = 3$ bands/images of size $P \times Q$ such that:
    - $b$ = number of bands/images, where $b \in \mathbb{Z}^+$
    - $P$ = number of rows, where $P \in \mathbb{Z}^+$
    - $Q$ = number of columns, where $Q \in \mathbb{Z}^+$
    - $B_i$ = the i-th band/image, where $B_i$ is a matrix of size $P \times Q$
    - $\bar{B}$ = the set of all bands/images, where $\bar{B}$ is a matrix of size $b \times P \times Q$

Let C be the function that partitions the full wavelength space of possible photon wavelengths and gives us the band images as defined by the camera/sensors parameters/specs. That is C takes in a 3D vector of $R \times n \times m$ and outputs a 3D vector of $a \times n \times m$ where $a$ is the number of bands/images that the camera/sensor has. Let us call the actual mapping of wavelengths reflected by the surface of the earth $R$ which

Do we have to take into account just the set of possible wavelengths or do we leave it as all possible wavelengths? (ie: possible wavelengths of light go from 0 to infinity but the earth only reflects a certain range of wavelengths.)

Lets define the set of all possible wavelengths as $\Lambda = \{~0 \dots \infty$\} and the set of all possible wavelengths capturable by the sensor as $\Lambda_C = \{~\lambda_{min} \dots \lambda_{max}$\}. Then the resulting set of wavelengths represented by the bands is the set $\bar{\Lambda}_C = {\lambda_1, \lambda_2, \dots, \lambda_a}$ where $\lambda_i \in \Lambda_C$ and $\lambda_i \neq \lambda_j$ for $i \neq j$ and $a$ is the number of bands. 

---
<br>
<!-- Gemini Version of Writeup--->

#### Phase 1: The Continous 3D-Physical Reality (Ground Truth)

Before the satellite takes a picture we should be modeling the reality of the situation as a continous state of physics. Since we want to be as realistic as possible we want to take into account the Earth's topography and the full electromagentics spectrum.

- **Spatial Domain (Base):** 
    - Let $\Omega \subset \mathbb{R}^2$ be the continous spatial domain of the image with coordinates $(x, y)$. 
- **Topography:** 
    - Let $h(x, y)$ be the true continous height function of the Earth's surface at the coordinates $(x, y)$.
- **The 3D Surface Manifold (S):** 
    - Let $S = {(x, y, z) \in \mathbb{R}^3 | z = h(x, y), (x, y) \in \Omega}$
- **Spectral Domain:** 
    - Let $\Lambda = (0, \infty)$ be the continous spectrum of all possible photon wavelengths, with $\lambda_i \in \Lambda$.
- **The True Signal (L):** 
    - Let $L = f(S, \Lambda)$ be the true spectral radiance reflecting off the 3D point at coordinates $(x, y, h(x, y))$ and wavelength $\lambda_i$.

#### Phase 2: Raw Image Capture (The 3D-to-2D Sensor Model)
The sensors discretize the continuous 3D reality into 2D matrices. The integration occurs over the warped surface area of the terrain, not a flat plane. 

Let $dA$ be the surface area element on S, defined as $dA= \sqrt{1+(∇h)^2}dxdy$.

- Hardware Specifications: Sat. A captures $a$ bands/images of size $n \times m$ and Sat. B captures $b$ bands/images of size $p \times q$ such that: 
    - $a, b \in \mathbb{Z}^+$
    - $n, m, p, q \in \mathbb{Z}^+$
- Sensor Footprints: 
    - Let $S^A_{i,j}$ and $S^B_{i,j}$ be the specific physical surface patches on S intersected by the instantaneous field of view (IFOV) of the $i$-th pixel of the $j$-th band for Sat. A and Sat. B respectively. 
- Spectral Response: 
    - Let $R^(k)_A(\lambda)$ and $R^(k)_B(\lambda)$ be the spectral response functions for the k-th band of Sat. A and Sat. B respectively. 

The raw capture tensors, $\bar{A}_{raw} \in \mathbb{R}^{a \times n \times m}$ and $\bar{B}_{raw} \in \mathbb{R}^{b \times p \times q}$ are defined element-wise for band $k$ and pixel $(i, j)$ as:

- $A^{(k,i,j)}_{raw} = P_A(\int_\Lambda(\int\int_{S^A_{i,j}} L(x, y, h(x, y), \lambda) \cdot dA) \cdot R^(k)_A(\lambda) \cdot d\lambda) + \mathcal{N}_A$

- $B^{(k,i,j)}_{raw} = P_B(\int_\Lambda(\int\int_{S^B_{i,j}} L(x, y, h(x, y), \lambda) \cdot dB) \cdot R^(k)_B(\lambda) \cdot d\lambda) + \mathcal{N}_B$

(Where $P$ is the signal-dependent Poisson shot noise, and $\mathcal{N}$ is the Gaussian read noise).

Phase 3: Pre-processing and Co-registration (Orthorectification)
To compare the disparate raw matrices they must be projected intoa shared coordinate system using an estimated Digital Elevation Model (DEM), $\hat{h}(x, y)$ which is an imperfect representation of the true topography $h(x, y)$. 

- Target Space: We defined a unified, resampled vector space $\mathbb{R}^{a \times N \times M}$ where $N$ and $M$ are the dimensions of the target space. 

- **Transformation Operators:**:
    - Let $\mathcal{T}_A$ and $\mathcal{T}_B$ be the orthorectification and resampling algorithms that attempt to flatten the 3D perspective and align the pixels for Sat. A and Sat. B respectively. 
- **Residual Error:**:
    - Because $\hat{h} \neq h$ and interpolation is a lossy process there will be a residual error $\mathcal{E_A}$ and $\mathcal{E_B}$

The final aligned tensors ready for analysis are:

- $\bar{A} = \mathcal{T}_A(\bar{A}_{raw}) + \mathcal{E_A}$
- $\bar{B} = \mathcal{T}_B(\bar{B}_{raw}) + \mathcal{E_B}$

Where both $\bar{A}, \bar{B} \in \mathbb{R}^{a \times N \times M}$. (This is assuming that $b = a$ now).

#### Phase 4: The Difference Metrics

With perfectly dimensionsed and aligned tesnsors we evaluate similarity and detect anomalies using four mathematical forumlations:

1. **The Difference Tensor ($\Delta$):**
    - An $a \times N \times M$ tensor that represents the absolute difference between the two tensors. Used to visually or algorithmically locate where anomalies or alignment failures exist.
    - $\Delta = \bar{A} - \bar{B}$

2. **The Frobenius Norm ($\mathcal{F}$):**
    - A scalar value that represents the magnitude of the difference between the two tensors. Used to determine if the difference is significant enough to be considered an anomaly.
    - $\mathcal{F} = \sqrt{\sum_{i=1}^{a}\sum_{j=1}^{N}\sum_{k=1}^{M}(\bar{A}^{(i,j,k)} - \bar{B}^{(i,j,k)})^2}$

3. **Mean Squared Error (MSE):**
    - A scalar value that represents the average squared difference between the two tensors. Used to determine if the difference is significant enough to be considered an anomaly.
    - $MSE = \frac{1}{aNM}\sum_{i=1}^{a}\sum_{j=1}^{N}\sum_{k=1}^{M}(\bar{A}^{(i,j,k)} - \bar{B}^{(i,j,k)})^2$

4. **Spectral Angle Mapper (SAM):**
    - A scalar value that represents the angle between the two tensors. Used to determine if the difference is significant enough to be considered an anomaly.
    - $SAM = \frac{1}{aNM}\sum_{i=1}^{a}\sum_{j=1}^{N}\sum_{k=1}^{M}(\bar{A}^{(i,j,k)} - \bar{B}^{(i,j,k)})^2$