PTW

!Mercury MoM input file, VIE/SIE Version 4.x compatible (VIE/Dual Sided SIE)

&MM_MOM
  bUseACA = .TRUE.,
  bSolve_ACA = .TRUE.,
  bOutOfCore = .TRUE.,
  bNormalizeToWaveLength = .FALSE.,
  bNormalize             = .FALSE.,
  dCloseLambda  = 0.100000,
  ACA_Factor_Tol = 0.000010,
  ACA_RHS_Tol = 0.000100,
  Point_Tolerance = 0.001000,
  nLargestBlockSize = -1,
  MemorySize_GB = -1.000000,
  stackSize_GB = -1.000000,
  nFillThreads = -1,
  nFillMKLThreads = 1,
  nLUThreads = -1,
  nLUMKLThreads = 1,
  nRHSThreads = 1,
  nRHSMKLThreads = 1,
  bOutputACAGrouping     = .FALSE.,
  bOutputRankFraction    = .FALSE.,
  bLimitLUColumns        = .FALSE.,
  Lop_Admissibility = WEAK,
  Kop_Admissibility = CLOSE
/

&Scratch_Memory
  Scratch_RankFraction_Z     = 0.300000,
  Scratch_RankFraction_LU    = 0.600000,
  Scratch_RankFraction_RHS   = 0.500000,
  Scratch_RankFraction_Solve = 1.000000,
  MemoryFraction_Z           = 0.950000,
  MemoryFraction_Scratch_LU  = 0.500000,
  MemoryFraction_LU          = 1.000000,
  MemoryFraction_RHS         = 0.500000,
  MemoryFraction_Solve       = 0.900000,
/

&QUADRATURE
  NTRISELF    = 7,
  NTRINEAR    = 3,
  NTRIFAR     = 3,
  NTETSELF    = 11,
  NTETNEAR    = 4,
  NTETFAR     = 4,
  NQGAUSS  = 4,
/

FREQUENCY
  ghz
  0.003000  0.030000  28   !Freq Start, Freq Stop, Number of Frequencies

Excitation
  MONOSTATIC

Angle Cut
  1
  0.000000  360.000000  361
  AZIMUTH
  90.000000

Boundary Conditions
PTW-Materials.lib
4
V_FREE_SPACE => Free_Space
V_PEC => PEC
V_PMC => PMC
V_NULL => NULL
1
0 BC_PEC V_FREE_SPACE

SIE
PTW.facet
mm

Geometry_End
