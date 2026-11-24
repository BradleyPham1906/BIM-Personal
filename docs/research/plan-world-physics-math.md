# The World Engine's mathematics: how a physicist and a mathematician would build it

Status: companion to `plan-world-physics.md`, for the owner's decisions (part 9). Written 2026-11-23.
Every formula here becomes one pure function and one reference test before it reaches the page; each phase's research
note re-reads it in its primary source (P) under `research-protocol.md` before the code uses it.

## 1. How they would think

A game programmer asks "what makes this look right?". A physicist asks "what is conserved, and what does the material
do?". A mathematician asks "is the problem well posed, and does the method converge to its answer?". The World Engine
needs all three questions answered in that order.

### 1.1 The physicist's recipe (the same for every phenomenon)

1. **Choose the scale and the model.** Form the dimensionless numbers (part 7) first: they decide which terms matter.
   Wind past a building at Re = 10^7 is turbulent; a slab under load is static; a dropped cube is rigid.
2. **Write the conservation law in integral form**, over any piece of the world $\Omega$ with boundary $\partial\Omega$:

   $$\frac{d}{dt}\int_\Omega u\,dV + \oint_{\partial\Omega} \mathbf{F}\cdot\mathbf{n}\,dA = \int_\Omega s\,dV$$

   The amount inside changes by what flows through the boundary and what is made inside. Mass, momentum, angular
   momentum and energy all take this form.
3. **Apply the divergence theorem** (Gauss), $\oint_{\partial\Omega}\mathbf{F}\cdot\mathbf{n}\,dA = \int_\Omega \nabla\cdot\mathbf{F}\,dV$,
   and since $\Omega$ is arbitrary, the local law follows:

   $$\frac{\partial u}{\partial t} + \nabla\cdot\mathbf{F} = s$$

4. **Close it with a constitutive law**: how this material relates flux to state (Hooke, Fourier, Fick, Darcy,
   Newtonian viscosity, Coulomb friction). Conservation is universal; constitutive laws are where materials differ.
   They are tensors, because a material's answer must not depend on the axes we chose (part 2).
5. **State boundary and initial conditions.** A fixed support, a heat flux, a wall the water cannot cross.
6. **Check invariances.** Galilean and rotational invariance, symmetries, and by Noether's theorem the quantities
   that must stay conserved: these become tests.

### 1.2 The mathematician's checks

1. **Well-posedness** (Hadamard): a solution exists, is unique, and depends continuously on the data. For linear
   elliptic problems Lax-Milgram gives this when the bilinear form is bounded and coercive.
2. **Weak form.** Multiply by a test function, integrate by parts (the divergence theorem again), and seek the
   solution in an energy space ($H^1$). This is what finite elements discretise.
3. **Discretisation that keeps the structure.** Conservative fluxes for conservation laws, symmetric positive
   definite matrices for energy problems, symplectic integrators for Hamiltonian motion.
4. **Convergence.** Lax equivalence: for a consistent scheme on a well-posed linear problem, stability is equivalent
   to convergence. Céa's lemma bounds the finite element error by the best approximation; for elements of degree
   $p$ the energy-norm error falls as $O(h^p)$.
5. **Conditioning.** A stiffness matrix's condition number grows like $h^{-2}$; preconditioning is not optional.
6. **Verification.** The observed order $p_{obs} = \ln(e_1/e_2)/\ln(h_1/h_2)$ must match the theory, on closed-form
   cases and on manufactured solutions (part 8).

### 1.3 The insight that shapes the build

Every phenomenon the plan lists reduces to **one of six mathematical archetypes**. Build each archetype's solver
once, verify it once, and each physical domain becomes only a constitutive law, coefficients and boundary conditions.

| Archetype | Model equation | Domains that use it |
|---|---|---|
| Elliptic (equilibrium) | $-\nabla\cdot(\mathbf{k}\nabla u) = f$ | Statics of solids, plates and frames; steady heat; groundwater; potential flow |
| Parabolic (diffusion) | $\partial_t u = \nabla\cdot(\mathbf{k}\nabla u) + f$ | Transient heat, consolidation of soil, moisture, smoke dilution |
| Hyperbolic (waves and transport) | $\partial_t u + \nabla\cdot\mathbf{F}(u) = s$ or $\ddot u = c^2\nabla^2 u$ | Structural dynamics, acoustics, shallow water, flood waves |
| Ordinary differential | $\dot{\mathbf{y}} = \mathbf{f}(\mathbf{y}, t)$ | Rigid bodies, vehicles, agents, modal coordinates, traffic |
| Eigenproblem | $\mathbf{K}\boldsymbol\phi = \lambda\mathbf{M}\boldsymbol\phi$ | Modes, buckling, principal stresses, principal axes of inertia |
| Constrained and complementarity | $\min \Pi(\mathbf{x})$ s.t. $\mathbf{g}(\mathbf{x}) \ge 0$; $0 \le \lambda \perp g \ge 0$ | Contact and friction, joints, form-finding, sketch constraints |

Kinetic methods (lattice Boltzmann, part 5.3) are a seventh route to the hyperbolic and parabolic archetypes.

## 2. Tensors: the language of the whole engine

A tensor is a multilinear map that is the same object in every basis; only its components change. Under a rotation
$\mathbf{R}$ (orthogonal, $\mathbf{R}\mathbf{R}^\top = \mathbf{I}$, $\det\mathbf{R} = 1$) the components transform as

$$T'_{i_1\ldots i_k} = R_{i_1 j_1}\cdots R_{i_k j_k}\,T_{j_1\ldots j_k}, \qquad \text{for rank 2:}\quad \boldsymbol\sigma' = \mathbf{R}\boldsymbol\sigma\mathbf{R}^\top$$

This is why the math core must hold tensors, not loose arrays: a wall can be rotated in the model, a timber panel's
grain can run in any direction, and the physics must not care.

### 2.1 The tensors the World Engine uses

| Rank | Components in 3D | Tensors in the app |
|---|---|---|
| 0 | 1 | Temperature $T$, pressure $p$, density $\rho$, mass $m$, water depth $h$, sound pressure level |
| 1 | 3 | Position $\mathbf{x}$, velocity $\mathbf{v}$, force $\mathbf{f}$, heat flux $\mathbf{q}$, traction $\mathbf{t}$, angular velocity $\boldsymbol\omega$ |
| 2 | 9 (6 if symmetric) | Stress $\boldsymbol\sigma$, strain $\boldsymbol\varepsilon$, inertia $\mathbf{I}$, rotation $\mathbf{R}$, deformation gradient $\mathbf{F}$, conductivity $\mathbf{k}$ (anisotropic), permeability |
| 4 | 81 (21 with symmetries) | Elasticity $\mathbb{C}$: 21 for general anisotropy, 9 orthotropic (timber, CLT), 5 transversely isotropic (fibre composites), 2 isotropic (steel, concrete) |

### 2.2 Stress: the screenshot's tensor, put to work

Cauchy's theorem: the traction on any face with unit normal $\mathbf{n}$ is

$$\mathbf{t}^{(\mathbf{n})} = \boldsymbol\sigma^\top\mathbf{n}, \qquad t_j = \sigma_{ij}\,n_i$$

(row $i$ the face normal, column $j$ the force component). Balance of angular momentum makes $\boldsymbol\sigma$
symmetric, so $\mathbf{t} = \boldsymbol\sigma\mathbf{n}$ and six numbers suffice. Stored in Voigt order
$[\sigma_{xx},\sigma_{yy},\sigma_{zz},\sigma_{yz},\sigma_{xz},\sigma_{xy}]$.

**Principal stresses** are the eigenvalues of $\boldsymbol\sigma$ (the archetype eigenproblem), their axes the
eigenvectors. **Invariants** (basis independent, so they are what checks and colours use):

$$I_1 = \operatorname{tr}\boldsymbol\sigma,\quad I_2 = \tfrac12\left[(\operatorname{tr}\boldsymbol\sigma)^2 - \operatorname{tr}(\boldsymbol\sigma^2)\right],\quad I_3 = \det\boldsymbol\sigma$$

Deviatoric stress $\mathbf{s} = \boldsymbol\sigma - \tfrac13 I_1\mathbf{I}$, $J_2 = \tfrac12\,\mathbf{s}:\mathbf{s}$, and the von Mises stress
used for steel yielding

$$\sigma_{vm} = \sqrt{3J_2} = \sqrt{\tfrac12\left[(\sigma_1-\sigma_2)^2 + (\sigma_2-\sigma_3)^2 + (\sigma_3-\sigma_1)^2\right]}$$

### 2.3 Rotations

Rotations form the group SO(3). Four representations, each with a job:

- **Matrix** $\mathbf{R}$: applying to points and tensors. Rodrigues, for axis $\hat{\mathbf{k}}$ and angle $\theta$:
  $\mathbf{R} = \mathbf{I} + \sin\theta\,\mathbf{K} + (1-\cos\theta)\,\mathbf{K}^2$, with $\mathbf{K}$ the cross-product matrix of $\hat{\mathbf{k}}$.
- **Euler angles** $R = R_z(\psi)R_y(\theta)R_x(\phi)$: what a person types. They have gimbal lock at $\theta = \pm 90°$,
  so never stored.
- **Unit quaternion** $q = (\cos\tfrac\theta2,\ \hat{\mathbf{k}}\sin\tfrac\theta2)$: what is stored and integrated. No
  gimbal lock, four numbers, cheap to renormalise; $q$ and $-q$ are the same rotation. Interpolation by slerp.
- **Axis-angle / rotation vector** $\boldsymbol\theta = \theta\hat{\mathbf{k}}$: small increments, the solver's unknowns.

Tests every implementation must pass: $\mathbf{R}\mathbf{R}^\top = \mathbf{I}$, $\det\mathbf{R} = 1$, round trips
$q \to \mathbf{R} \to q$ (up to sign) and Euler $\to \mathbf{R} \to$ Euler away from gimbal lock.

## 3. Calculus on the model's own geometry

### 3.1 Mass properties from the divergence theorem

For a closed, consistently oriented triangle mesh, choose $\mathbf{F} = \mathbf{x}/3$ so $\nabla\cdot\mathbf{F} = 1$:

$$V = \int_\Omega dV = \frac13\oint_{\partial\Omega}\mathbf{x}\cdot\mathbf{n}\,dA = \frac16\sum_{\triangle(\mathbf{a},\mathbf{b},\mathbf{c})}\mathbf{a}\cdot(\mathbf{b}\times\mathbf{c})$$

Each triangle and the origin form a signed tetrahedron; holes and concavities cancel exactly. Centre of mass:
$\mathbf{c} = \frac1V\sum_t V_t\,\frac{\mathbf{a}+\mathbf{b}+\mathbf{c}}{4}$. Inertia from the second-moment
(covariance) tensor, with $\mathbf{A}_t = [\mathbf{a}\ \mathbf{b}\ \mathbf{c}]$ as columns:

$$\mathbf{C} = \rho\sum_t \det(\mathbf{A}_t)\,\mathbf{A}_t\,\mathbf{C}_0\,\mathbf{A}_t^\top,\qquad \mathbf{C}_0 = \frac1{120}\begin{bmatrix}2&1&1\\1&2&1\\1&1&2\end{bmatrix},\qquad \mathbf{I}_O = \operatorname{tr}(\mathbf{C})\,\mathbf{I} - \mathbf{C}$$

which is the discrete form of $\mathbf{I} = \int\rho\,(|\mathbf{r}|^2\mathbf{I} - \mathbf{r}\otimes\mathbf{r})\,dV$. Move it to the
centre of mass with the parallel axis theorem, $\mathbf{I}_c = \mathbf{I}_O - m\,(|\mathbf{c}|^2\mathbf{I} - \mathbf{c}\otimes\mathbf{c})$,
and its eigenvectors are the principal axes. Checked against $\tfrac16 m a^2$ (cube), $\tfrac12 mr^2$ (cylinder axis),
$\tfrac25 mr^2$ (sphere), within the mesh's discretisation error.

### 3.2 Curvilinear coordinates and Jacobians (the cylinder screenshot)

Any mapping $\mathbf{x} = \mathbf{x}(\boldsymbol\xi)$ scales volume by $|\det\mathbf{J}|$, $J_{ij} = \partial x_i/\partial\xi_j$:
cylindrical $dV = r\,dr\,d\theta\,dz$, spherical $dV = r^2\sin\varphi\,dr\,d\theta\,d\varphi$. Finite elements use the same
rule: every element is a map from a reference element, and every integral over it is

$$\int_{\Omega_e} f\,dV = \int_{\hat\Omega} f(\mathbf{x}(\boldsymbol\xi))\,|\det\mathbf{J}(\boldsymbol\xi)|\,d\hat V \approx \sum_g w_g\,f(\mathbf{x}(\boldsymbol\xi_g))\,|\det\mathbf{J}(\boldsymbol\xi_g)|$$

Gauss-Legendre with $n$ points is exact for polynomials of degree $2n-1$ on a line; the triangle and tetrahedron have
their own symmetric rules. The Riemann sum in the screenshot is the zeroth-order version of this.

### 3.3 Differential operators on meshes and grids

| Operator | Continuous | Discrete form used |
|---|---|---|
| Gradient | $\nabla u$ | Per triangle, constant; on grids, central differences $(u_{i+1}-u_{i-1})/2h$ |
| Divergence | $\nabla\cdot\mathbf{F}$ | Finite volume: $\frac1{V_i}\sum_f \mathbf{F}_f\cdot\mathbf{n}_f A_f$ (conservative by construction) |
| Curl | $\nabla\times\mathbf{F}$ | Circulation per face, $\frac1A\oint\mathbf{F}\cdot d\mathbf{l}$ (Stokes) |
| Laplacian | $\nabla^2 u$ | Cotangent formula on triangles, $\frac1{2A_i}\sum_j(\cot\alpha_{ij}+\cot\beta_{ij})(u_j-u_i)$; 5 or 7 point stencil on grids |
| Curvature | $\kappa_1,\kappa_2$, $H$, $K$ | Mean curvature from the cotangent Laplacian of position; Gaussian from the angle defect $2\pi - \sum\theta_j$ |

The four theorems of the third screenshot become tests: the gradient theorem ($\int_C\nabla F\cdot d\mathbf{p} = F(\mathbf{b}) - F(\mathbf{a})$),
Green's, Stokes' and the divergence theorem must hold for the discrete operators to rounding error on closed meshes.

### 3.4 Tangent planes and the Hessian (the second screenshot)

Linearisation $f(\mathbf{x}_0+\mathbf{v}) = f(\mathbf{x}_0) + \nabla f\cdot\mathbf{v} + \tfrac12\mathbf{v}^\top\mathbf{H}\mathbf{v} + O(|\mathbf{v}|^3)$
is the engine of every nonlinear solver: Newton's method solves $\mathbf{H}\,\Delta\mathbf{x} = -\nabla f$; the Jacobian of
the residual is the tangent stiffness; the Hessian of the terrain gives its curvature (V248) and the Hessian of the
potential energy decides stability (a structure buckles when it stops being positive definite).

## 4. Mechanics of solids and bodies

### 4.1 Rigid bodies (Newton-Euler)

$$m\,\dot{\mathbf{v}} = \mathbf{f},\qquad \mathbf{I}\dot{\boldsymbol\omega} + \boldsymbol\omega\times(\mathbf{I}\boldsymbol\omega) = \boldsymbol\tau\ \ \text{(body frame)},\qquad \dot q = \tfrac12\,\boldsymbol\omega\otimes q\ \ \text{(world frame)}$$

The gyroscopic term $\boldsymbol\omega\times\mathbf{I}\boldsymbol\omega$ is why a thrown book tumbles about its middle axis
(the intermediate axis theorem): a test that a naive integrator fails and a correct one passes.

**Contact** (Signorini) and **friction** (Coulomb), with gap $g_n$, normal impulse $\lambda_n$, tangential $\boldsymbol\lambda_t$:

$$0 \le g_n \perp \lambda_n \ge 0,\qquad \|\boldsymbol\lambda_t\| \le \mu\lambda_n,\qquad v_n^+ = -e\,v_n^-$$

Bodies cannot interpenetrate, push but never pull, and slide only when friction saturates; $e$ is restitution. A
block on a slope of angle $\alpha$ holds while $\mu \ge \tan\alpha$ (the plan's T2). Jolt solves this complementarity
problem with sequential impulses; our tests check its answers against these laws.

### 4.2 Linear elasticity

Balance of momentum, small strain, and Hooke's law (the rank 4 tensor):

$$\nabla\cdot\boldsymbol\sigma + \mathbf{b} = \rho\ddot{\mathbf{u}},\qquad \boldsymbol\varepsilon = \tfrac12(\nabla\mathbf{u} + \nabla\mathbf{u}^\top),\qquad \boldsymbol\sigma = \mathbb{C}:\boldsymbol\varepsilon$$

Isotropic: $\boldsymbol\sigma = \lambda\operatorname{tr}(\boldsymbol\varepsilon)\mathbf{I} + 2\mu\boldsymbol\varepsilon$, with
$\lambda = \frac{E\nu}{(1+\nu)(1-2\nu)}$, $\mu = G = \frac{E}{2(1+\nu)}$. Thermal strain adds $\alpha\,\Delta T\,\mathbf{I}$.

**Weak form** (the principle of virtual work), for every admissible $\delta\mathbf{u}$:

$$\int_\Omega \boldsymbol\sigma:\delta\boldsymbol\varepsilon\,dV = \int_\Omega \mathbf{b}\cdot\delta\mathbf{u}\,dV + \int_{\Gamma_t}\bar{\mathbf{t}}\cdot\delta\mathbf{u}\,dA$$

Discretised: $\mathbf{K}\mathbf{u} = \mathbf{f}$ with $\mathbf{K}_e = \int_{\Omega_e}\mathbf{B}^\top\mathbf{D}\mathbf{B}\,|\det\mathbf{J}|\,d\hat V$.
Equivalently, the solution minimises the potential energy $\Pi = \tfrac12\int\boldsymbol\sigma:\boldsymbol\varepsilon\,dV - W_{ext}$.

**Reduced models** (what the frame solve and plates use, each a special case of the above):

| Element | Equation | Notes |
|---|---|---|
| Bar | $EA\,u'' + p = 0$ | Trusses, cables in tension |
| Euler-Bernoulli beam | $EI\,w'''' = q$ | The frame solve's members (V125) |
| Timoshenko beam | adds shear $\kappa GA$ | Deep beams, transfer girders |
| Kirchhoff plate | $D\nabla^4 w = q$, $D = \frac{Eh^3}{12(1-\nu^2)}$ | Thin slabs, walls out of plane |
| Mindlin-Reissner plate | adds transverse shear | Thick slabs; what shell elements use |
| Euler buckling | $P_{cr} = \frac{\pi^2EI}{(KL)^2}$ | Checks column and member stability |

### 4.3 Structural dynamics

$$\mathbf{M}\ddot{\mathbf{u}} + \mathbf{C}\dot{\mathbf{u}} + \mathbf{K}\mathbf{u} = \mathbf{f}(t) = -\mathbf{M}\mathbf{r}\,\ddot u_g(t)\ \text{(ground motion)}$$

Modes: $\mathbf{K}\boldsymbol\phi_n = \omega_n^2\mathbf{M}\boldsymbol\phi_n$, $T_n = 2\pi/\omega_n$, mass-normalised
$\boldsymbol\phi^\top\mathbf{M}\boldsymbol\phi = 1$. Rayleigh damping $\mathbf{C} = \alpha\mathbf{M} + \beta\mathbf{K}$, giving
$\zeta_n = \frac{\alpha}{2\omega_n} + \frac{\beta\omega_n}{2}$. Modal superposition $\mathbf{u} = \sum_n\boldsymbol\phi_n y_n(t)$ turns the system
into independent oscillators $\ddot y_n + 2\zeta_n\omega_n\dot y_n + \omega_n^2 y_n = \Gamma_n\ddot u_g$: this is how the live
world sways a building in real time (plan V289) while Newmark (V245) gives the reference.

### 4.4 Large deformation (later)

$\mathbf{F} = \mathbf{I} + \nabla_{\mathbf{X}}\mathbf{u}$, Green-Lagrange strain $\mathbf{E} = \tfrac12(\mathbf{F}^\top\mathbf{F} - \mathbf{I})$,
polar decomposition $\mathbf{F} = \mathbf{R}\mathbf{U}$ separating rotation from stretch. Needed for cables, membranes
(V246), collapse and soft bodies; frame-indifferent by construction.

## 5. Fluids, heat, sound, light

### 5.1 Fluid flow

Mass and momentum for an incompressible Newtonian fluid (Navier-Stokes):

$$\nabla\cdot\mathbf{u} = 0,\qquad \rho\left(\frac{\partial\mathbf{u}}{\partial t} + (\mathbf{u}\cdot\nabla)\mathbf{u}\right) = -\nabla p + \mu\nabla^2\mathbf{u} + \rho\mathbf{g}$$

with the stress tensor $\boldsymbol\sigma = -p\mathbf{I} + 2\mu\mathbf{D}$, $\mathbf{D} = \tfrac12(\nabla\mathbf{u}+\nabla\mathbf{u}^\top)$.
Forces on bodies: dynamic pressure $q = \tfrac12\rho V^2$ (ASCE 7 writes $q_z = 0.613K_zK_{zt}K_eV^2$ in N/m²), drag
$F_D = \tfrac12\rho C_D A v^2$, buoyancy $F_B = \rho_f g V_{sub}$ (Archimedes; the swimmer and floating objects).
Atmospheric boundary layer: $u(z) = \frac{u_*}{\kappa}\ln\frac{z}{z_0}$, $\kappa \approx 0.41$.

### 5.2 Water on the ground (shallow water equations)

Depth-averaged mass and momentum, with bed elevation $b$ and Manning friction:

$$\partial_t h + \nabla\cdot(h\mathbf{u}) = r - i,\qquad \partial_t(h\mathbf{u}) + \nabla\cdot\left(h\mathbf{u}\otimes\mathbf{u} + \tfrac12 g h^2\mathbf{I}\right) = -gh\nabla b - g\,\frac{n^2|\mathbf{u}|\mathbf{u}}{h^{1/3}}$$

($r$ rain, $i$ infiltration). A hyperbolic conservation law: finite volumes with an approximate Riemann solver
(HLL), a well-balanced scheme so a lake at rest stays at rest, and the CFL limit with wave speed $|\mathbf{u}| + \sqrt{gh}$.
Steady channel flow reduces to Manning, $V = \frac1n R^{2/3}S^{1/2}$; peak runoff to the rational method $Q = C\,i\,A$ (SI).

### 5.3 Lattice Boltzmann (the wind solver, V221)

Particle distributions $f_i$ stream along lattice velocities $\mathbf{c}_i$ and relax to equilibrium (BGK):

$$f_i(\mathbf{x}+\mathbf{c}_i\Delta t,\,t+\Delta t) = f_i - \frac{1}{\tau}\left(f_i - f_i^{eq}\right),\qquad f_i^{eq} = w_i\rho\left[1 + \frac{\mathbf{c}_i\cdot\mathbf{u}}{c_s^2} + \frac{(\mathbf{c}_i\cdot\mathbf{u})^2}{2c_s^4} - \frac{\mathbf{u}\cdot\mathbf{u}}{2c_s^2}\right]$$

$\rho = \sum f_i$, $\rho\mathbf{u} = \sum f_i\mathbf{c}_i$, $c_s^2 = \tfrac13$, viscosity $\nu = c_s^2(\tau - \tfrac12)\Delta t$. Its
moments recover Navier-Stokes (Chapman-Enskog). Local and explicit, so it maps onto WebGPU (V219, V294).

### 5.4 Heat

$$\rho c_p\frac{\partial T}{\partial t} = \nabla\cdot(\mathbf{k}\nabla T) + \dot q,\qquad \mathbf{q} = -\mathbf{k}\nabla T\ \text{(Fourier)}$$

Surfaces: convection $q = h(T_s - T_\infty)$, radiation $q = \varepsilon\sigma_{SB}(T_s^4 - T_{sur}^4)$. Steady layered wall:
$U = 1/(R_{si} + \sum_j d_j/k_j + R_{se})$ (ISO 6946). Thermal mass: the diffusion time of a layer $\sim d^2/\alpha$,
$\alpha = k/\rho c_p$. Parabolic: implicit time stepping, or explicit under $\Delta t \le \Delta x^2/(2d\,\alpha)$.

### 5.5 Sound

$$\nabla^2 p - \frac{1}{c^2}\frac{\partial^2 p}{\partial t^2} = 0,\qquad L_p = 20\log_{10}\frac{p_{rms}}{20\,\mu\text{Pa}}$$

Free field point source: $L_p = L_W - 20\log_{10}r - 11$ dB. Rooms, statistically: Sabine $T_{60} = 0.161\,V/A$,
$A = \sum\alpha_iS_i$; Eyring $T_{60} = 0.161\,V/(-S\ln(1-\bar\alpha))$ for absorbent rooms. Transmission between rooms
by the mass law, about 6 dB more insulation per doubling of surface mass.

### 5.6 Light

Irradiance from the sun on a surface $E = E_{dn}\cos\theta_i$, with $\cos\theta_i = \mathbf{n}\cdot\hat{\mathbf{s}}$ from the sun
vector (V107); a point source $E = I\cos\theta/r^2$. Reflection at a surface: Fresnel, approximated by Schlick
$R(\theta) = R_0 + (1-R_0)(1-\cos\theta)^5$ (V220). The rendering equation $L_o = L_e + \int_{\Omega}f_r\,L_i\cos\theta\,d\omega$
is what Radiance (via Ladybug) solves for daylight.

## 6. Ground, people, vehicles, Earth

### 6.1 Soil

Effective stress $\boldsymbol\sigma' = \boldsymbol\sigma - u_w\mathbf{I}$ (Terzaghi). Strength, Mohr-Coulomb: $\tau_f = c' + \sigma'\tan\phi'$.
Bearing capacity of a strip footing: $q_u = c'N_c + qN_q + \tfrac12\gamma BN_\gamma$. Consolidation: $\partial_t u_w = c_v\,\partial_z^2 u_w$
(parabolic) and settlement $s = \frac{C_cH}{1+e_0}\log_{10}\frac{\sigma'_0+\Delta\sigma}{\sigma'_0}$. Groundwater: Darcy
$\mathbf{q} = -\mathbf{K}\nabla h$ with $\nabla\cdot\mathbf{q} = 0$ (elliptic). Slope stability: Bishop's factor of safety as a fixed point.

### 6.2 People

Social force model (Helbing and Molnar 1995; Helbing, Farkas and Vicsek 2000):

$$m_i\frac{d\mathbf{v}_i}{dt} = m_i\frac{v_i^0\mathbf{e}_i - \mathbf{v}_i}{\tau_i} + \sum_{j\ne i}\mathbf{f}_{ij} + \sum_W\mathbf{f}_{iW},\qquad \mathbf{f}_{ij} = A_i\,e^{(r_{ij}-d_{ij})/B_i}\,\mathbf{n}_{ij} + \text{contact terms}$$

Desired direction $\mathbf{e}_i$ from the shortest path on the navigation mesh (Dijkstra, A*) or the eikonal equation
$|\nabla\phi| = 1/f(\rho)$. Validated against the fundamental diagram (speed against density) and door flow rates.

### 6.3 Vehicles

Car following, the Intelligent Driver Model (have, V171):
$\dot v = a\left[1 - (v/v_0)^\delta - (s^*/s)^2\right]$, $s^* = s_0 + vT + \frac{v\Delta v}{2\sqrt{ab}}$.
Braking distance $d = v\,t_r + \frac{v^2}{2g(\mu \pm G)}$ on grade $G$ (T4). Tyre force, Pacejka's magic formula
$F = D\sin\left(C\arctan\left(B\kappa - E(B\kappa - \arctan B\kappa)\right)\right)$; Jolt's wheeled vehicle supplies its own.
Kinematic bicycle model for steering paths: $\dot\psi = \frac{v}{L}\tan\delta$.

### 6.4 The Earth

Geodetic to Earth-centred (WGS 84): $N = a/\sqrt{1-e^2\sin^2\varphi}$, $X = (N+h)\cos\varphi\cos\lambda$,
$Y = (N+h)\cos\varphi\sin\lambda$, $Z = (N(1-e^2)+h)\sin\varphi$; then a rotation to the site's local east-north-up frame,
which is the world's frame. Standard gravity $g_0 = 9.80665$ m/s² as a registry value, local gravity a later edition.

## 7. Choosing the model: dimensionless numbers

The physicist's first step, and the justification for simulation level of detail: the numbers say which terms
can be dropped, so cheaper models far from the viewer are physics, not cheating.

| Number | Definition | What it decides |
|---|---|---|
| Reynolds | $Re = \rho VL/\mu$ | Laminar or turbulent flow; whether viscosity matters |
| Froude | $Fr = V/\sqrt{gL}$ | Sub- or supercritical water flow; wave regime |
| Mach | $Ma = V/c$ | Incompressible below about 0.3 (all building wind) |
| Courant (CFL) | $C = \lvert u\rvert\Delta t/\Delta x$ | Largest stable explicit time step |
| Peclet | $Pe = VL/\alpha$ | Whether heat or smoke is carried or diffuses |
| Biot | $Bi = hL/k$ | Whether a body can be one temperature (lumped) |
| Slenderness | $KL/r$ | Beam theory or buckling governs |
| Period ratio | $T_n/\Delta t$ | Time step needed to resolve a structure's mode |

## 8. Numerical methods and how they are verified

### 8.1 Time integration

| Method | Update | Use |
|---|---|---|
| Semi-implicit (symplectic) Euler | $\mathbf{v}_{n+1} = \mathbf{v}_n + \Delta t\,\mathbf{a}(\mathbf{x}_n)$; $\mathbf{x}_{n+1} = \mathbf{x}_n + \Delta t\,\mathbf{v}_{n+1}$ | Real-time bodies: energy bounded, never explodes |
| Velocity Verlet | $\mathbf{x}_{n+1} = \mathbf{x}_n + \Delta t\mathbf{v}_n + \tfrac12\Delta t^2\mathbf{a}_n$; $\mathbf{v}_{n+1} = \mathbf{v}_n + \tfrac12\Delta t(\mathbf{a}_n + \mathbf{a}_{n+1})$ | Particles, cables, crowds; second order |
| RK4 | four stages, $O(\Delta t^4)$ | Smooth ODEs: vehicles, sun paths, reference solutions |
| Newmark ($\beta = \tfrac14$, $\gamma = \tfrac12$) | average acceleration | Structural dynamics; unconditionally stable, no numerical damping |
| Generalised-alpha | Newmark plus controlled high-frequency damping | Stiff structures, contact |
| Backward Euler / Crank-Nicolson | implicit | Heat and consolidation |

### 8.2 Solving the systems

Dense LU and Cholesky for small systems; banded Cholesky with Reverse Cuthill-McKee (have, V125); sparse Cholesky
and conjugate gradient with an incomplete Cholesky or multigrid preconditioner for finite elements, heat and pressure;
Newton with line search for nonlinear problems; Jacobi, subspace iteration and Lanczos for eigenproblems; projected
Gauss-Seidel for complementarity (inside Jolt).

### 8.3 Verification ladder (every solver climbs it before wiring)

1. **Identities and conservation**: mass, momentum, angular momentum and energy to rounding (or to the method's
   known dissipation); $\mathbf{R}\mathbf{R}^\top = \mathbf{I}$; symmetric stiffness; the divergence theorem on closed meshes.
2. **Closed-form cases**: free fall, the pendulum's period, a cantilever's tip deflection $PL^3/3EI$, a simply
   supported plate (Navier series), the 1D heat equation's error function, the dam break (Ritter), Poiseuille flow.
3. **Method of manufactured solutions**: choose $u^*$, compute the source $f = \mathcal{L}u^*$, solve, and measure the
   observed convergence order on refined meshes; it must equal the theoretical one.
4. **Published benchmarks**: NAFEMS LE1 to LE10 for elasticity, flow past a cylinder (Strouhal about 0.2), the
   lid-driven cavity (Ghia et al. 1982), door flow rates for crowds.
5. **Cross-check against an established program** where its output can be read as data.

## 9. What this changes in the plan, and the owner's decisions

The plan's Stage A (`plan-world-physics.md` part 5) becomes five phases, built around the archetypes:

| Phase | What | Pass when |
|---|---|---|
| V277a | Tensors and rotations: vec3, mat3, mat4, quaternion, symmetric rank 2 in Voigt form, isotropic and orthotropic rank 4, transformation $\mathbf{R}\boldsymbol\sigma\mathbf{R}^\top$, invariants, principal values, Euler, Rodrigues, slerp; units | Part 2's tests; old duplicates replaced |
| V277b | Calculus on geometry: divergence-theorem mass properties, quadrature (Gauss lines, triangles, tetrahedra), discrete gradient, divergence, curl, cotangent Laplacian, curvature | Part 3.1's solids; the four theorems on closed meshes |
| V277c | Linear algebra: dense LU, Cholesky, QR, SVD, Jacobi eigen; sparse storage, preconditioned CG, sparse Cholesky, Lanczos | Closed forms; a manufactured Poisson problem of 10,000 unknowns |
| V277d | Time integration: the six integrators of 8.1 behind one interface, with energy and momentum monitors | Each method's observed order; the intermediate-axis tumble |
| V277e | The archetype solvers: a finite element assembler for elliptic and parabolic problems, a finite volume conservation-law solver with HLL for hyperbolic ones, all generic in their coefficients | Part 8.3 rungs 1 to 3 for each |

Every later domain phase then supplies only its constitutive law, coefficients (registry data) and boundary
conditions to one of these solvers.

**Decisions for the owner** (in addition to `plan-world-physics.md` part 10):

1. **Archetypes first.** Build the six archetype solvers once (V277a to V277e) and express every domain through them.
   Recommended: yes.
2. **Tensors as first-class values.** Material laws, stress and inertia are tensors in the core, stored compactly
   (Voigt), with rotation handled by the core. Recommended: yes.
3. **The verification ladder is mandatory.** No solver is wired into the page until it passes rungs 1 to 3 at
   least, recorded in its research note. Recommended: yes.
4. **Orthotropic materials early.** Timber and CLT need the 9-constant elasticity tensor; include it in V277a.
   Recommended: yes.

## 10. References to be read in their primary sources (P) by each phase's research

Continuum mechanics and tensors: Gurtin, *An Introduction to Continuum Mechanics*; Malvern, *Introduction to the
Mechanics of a Continuous Medium*. Finite elements: Hughes, *The Finite Element Method*; Bathe, *Finite Element
Procedures*; Brenner and Scott for the convergence theory. Rigid bodies and contact: Goldstein, *Classical
Mechanics*; Stewart and Trinkle (1996) on complementarity contact; Catto's sequential impulses. Mass properties:
Mirtich (1996); Tonon (2004). Conservation laws: LeVeque, *Finite Volume Methods for Hyperbolic Problems*; Toro,
*Riemann Solvers and Numerical Methods for Fluid Dynamics*. Lattice Boltzmann: Kruger et al., *The Lattice Boltzmann
Method*. Discrete differential geometry: Meyer, Desbrun, Schroder and Barr (2003). Geometric integration: Hairer,
Lubich and Wanner. Verification: Roache, *Verification and Validation in Computational Science and Engineering*.
Heat: Incropera. Acoustics: Kuttruff, *Room Acoustics*. Soils: Das, *Principles of Geotechnical Engineering*.
Crowds: Helbing and Molnar (1995). Vehicles: Pacejka, *Tyre and Vehicle Dynamics*; Treiber and Kesting, *Traffic
Flow Dynamics*. Structural dynamics: Chopra, *Dynamics of Structures*. Standards as already in the registry
(ASCE 7-22, ACI 318-19, AISC 360-22, ISO 6946).
