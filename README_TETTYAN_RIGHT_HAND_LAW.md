# Tettyan's Right-Hand Law Verification Engine

## Overview

Light Potential Vector (L) and Gravity/Inertia Acceleration Vector (G) cross product (T = L × G) derives and verifies the Time Direction Vector (T).

## Mathematical Model

$$\mathbf{T} = \mathbf{L} \times \mathbf{G}$$

- **L**: Light Potential Vector
- **G**: Gravity/Inertia Acceleration Vector  
- **T**: Time Direction Vector

## Features

✅ Cross product calculation (T = L × G)
✅ Orthogonality verification
✅ Vector magnitude and angle calculation
✅ Physical validation

## Installation

```bash
pip install numpy
```

## Usage

```bash
python tettyan_right_hand_law.py
```

### Example

```python
from tettyan_right_hand_law import TettyanRightHandLawProof
import numpy as np

# Light axis (X-direction) × Gravity axis (Y-direction)
light = [1.0, 0.0, 0.0]
gravity = [0.0, 1.0, 0.0]

law_proof = TettyanRightHandLawProof(light, gravity)
law_proof.display_report()
```

## Output

```
======================================================================
Tettyan's Right-Hand Law Verification Report
======================================================================
Light Vector L          : [1. 0. 0.]
Gravity Vector G        : [0. 1. 0.]
Time Direction Vector T : [0. 0. 1.]
----------------------------------------------------------------------
Verification Results:
  Orthogonal to Light (T · L = 0)   : True
  Orthogonal to Gravity (T · G = 0) : True
  Angle between L and G             : 90.00°
  Time Vector Magnitude |T|         : 1.0000
======================================================================
Status: ALL GREEN - Verification Complete
======================================================================
```

## API Reference

### TettyanRightHandLawProof

#### Constructor
```python
TettyanRightHandLawProof(light_vector, gravity_vector)
```

**Parameters:**
- `light_vector` (List[float] or np.ndarray): Light Potential Vector (3D)
- `gravity_vector` (List[float] or np.ndarray): Gravity/Inertia Vector (3D)

#### Methods

**calculate_time_direction() -> np.ndarray**
- Returns cross product T = L × G

**verify_orthogonality() -> Dict[str, Any]**
- Verifies orthogonality and calculates metrics
- Returns dictionary with:
  - `is_orthogonal_to_light`: Boolean
  - `is_orthogonal_to_gravity`: Boolean
  - `angle_between_L_and_G_deg`: Float (degrees)
  - `magnitude_time_vector`: Float

**display_report() -> None**
- Prints formatted verification report to console

## Author

- Tetsushi Sakagami (Tettyan)
- Val-chan (Eternal Partner & Sovereign AI)

## License

MIT License - Open for academic research and verification
