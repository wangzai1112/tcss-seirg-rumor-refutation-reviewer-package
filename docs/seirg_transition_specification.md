# SEIRG Transition Specification

Date: 2026-06-14

This note records the compact transition-equation specification used to document the coupled online-offline SEIRG model in the TCSS manuscript. It is a derivation and reproducibility aid. It does not replace the AnyLogic agent-based simulation, and it does not provide causal evidence about real-world policy effectiveness.

## State Variables

The baseline coupled SEIR model uses normalized state proportions:

- `s(t)`: susceptible or unaware individuals.
- `e(t)`: exposed individuals who have encountered the rumor but are not yet active spreaders.
- `i1(t)`: online spreaders.
- `i2(t)`: offline spreaders.
- `r(t)`: removed or immune individuals.

The SEIRG extension adds:

- `g1(t)`: online refutation-response state entered by individuals after online corrective information, prompts, fact checking, public clarification, or online rebuttal.
- `g2(t)`: offline refutation-response state entered by individuals after offline explanation or interpersonal clarification.

`g1(t)` and `g2(t)` are individual compartment proportions. They are not stocks of public-information volume, numbers of official messages, or direct measures of real-world implementation intensity. This interpretation is required for the conservation condition below.

The SEIRG conservation condition is:

```text
s(t) + e(t) + i1(t) + i2(t) + r(t) + g1(t) + g2(t) = 1.
```

## Baseline Coupled SEIR System

Let `beta1` and `beta2` denote online and offline propagation coefficients, `k1` and `k2` denote average contact levels, `sigma` denote latent-to-spreader conversion, `theta` denote the share entering the online-spreader state, `gamma1` and `gamma2` denote spreader exit rates, and `delta` denote return from `R` to `S`.

```text
ds/dt  = -(beta1*k1*i1 + beta2*k2*i2)*s + delta*r
de/dt  =  (beta1*k1*i1 + beta2*k2*i2)*s - sigma*e
di1/dt =  theta*sigma*e - gamma1*i1
di2/dt =  (1-theta)*sigma*e - gamma2*i2
dr/dt  =  gamma1*i1 + gamma2*i2 - delta*r
```

Around the rumor-free equilibrium, the model-based reproduction indicator is:

```text
R0 = theta*(beta1*k1/gamma1) + (1-theta)*(beta2*k2/gamma2).
```

For `L` layers, the corresponding layer-sum expression is:

```text
R0(L) = sum_l theta_l*(beta_l*k_l/gamma_l), with sum_l theta_l = 1.
```

## SEIRG Extension

The intervention switch is:

```text
h(t; Tg) = 0, if t < Tg
h(t; Tg) = 1, if t >= Tg
```

Let `alpha1` and `alpha2` denote direct online/offline refutation transition rates after the switch is active. Let `mu1` and `mu2` denote the interaction between accumulated refutation states and active spreaders. Let `rho` denote return or forgetting from `R`, `G1`, and `G2` to `S`.

A compact mean-field representation used for equation-level checking is:

```text
lambda(t) = beta1*k1*i1 + beta2*k2*i2

ds/dt  = -lambda(t)*s + rho*r + rho*g1 + rho*g2
de/dt  =  lambda(t)*s - sigma*e
di1/dt =  theta*sigma*e - gamma1*i1 - h(t;Tg)*alpha1*i1 - mu1*g1*i1
di2/dt =  (1-theta)*sigma*e - gamma2*i2 - h(t;Tg)*alpha2*i2 - mu2*g2*i2
dg1/dt =  h(t;Tg)*alpha1*i1 - rho*g1
dg2/dt =  h(t;Tg)*alpha2*i2 - rho*g2
dr/dt  =  gamma1*i1 + gamma2*i2 + mu1*g1*i1 + mu2*g2*i2 - rho*r
```

This form makes the manuscript's modeling assumptions explicit: refutation is represented as state flow and spreader-exit interaction, not as a direct subtraction from the outcome metric.

## Effective Indicator After Refutation

After refutation starts at `Tg`, the manuscript uses the following directional indicator:

```text
RE(Tg) = s(Tg) * [
  theta*(beta1*k1 / gamma1_tilde(Tg))
  + (1-theta)*(beta2*k2 / gamma2_tilde(Tg))
]
```

The effective exit terms are defined as:

```text
gamma1_tilde(Tg) = gamma1 + alpha1 + mu1*g1(Tg)
gamma2_tilde(Tg) = gamma2 + alpha2 + mu2*g2(Tg)
```

The `alpha` terms apply after the intervention switch is active, and the `mu` terms summarize contact with accumulated refutation-response states at the local state used for the directional indicator. This is a local model indicator. It should not be read as a real-world policy-effect estimate, a full nonlinear stability theorem, or a prediction of final propagation size.

## Relation to the Reproducibility Package

The standard-library reference implementation is provided as `scripts/analysis/mean_field_reference_seirg.py` in this package. That script is intended to verify state-flow direction, intervention timing, and the reported `R0`-style indicators. The manuscript's primary numerical results come from the AnyLogic agent-based simulation outputs, not from this mean-field reference script.
