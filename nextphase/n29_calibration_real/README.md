# N29 - Threshold calibration on real streams

## Reviewer issue
IEEE R2-7: verify-by-construction in Algorithm 2, wrong numbers in Remark 3, and a sample-complexity
result disconnected from the experiments.

## Corrected numbers for Remark 3
With gamma = 0.985 the burn-in 1/(1-gamma) is 66.7 steps (not 13); Eq. (14) with epsilon = delta = 0.05
asks for 1/(1-gamma) + ln(2/delta)/(2 epsilon^2) = 66.7 + 737.8 = 804 pilot steps (not 300). In the revised
protocol the beliefs are pre-warmed and the pilot keeps every step (no burn-in, CHANGES.md B9), and the
bound below replaces Eq. (14).

## Method
Pilots are contiguous blocks of a real honest run (target delta = 0.05); out-of-sample FPR is measured on
held-out honest episodes and OER on the matching sleeper episodes; 40 pilots per N.
* quantile eps=0: theta = delta-quantile of the pilot (no margin);
* quantile eps=0.05: the default Algorithm 2 (margin 0.05);
* min-of-pilot: the submitted rule.
* DKW bound: K (delta + sqrt(ln(2K/beta)/(2 N/tau_int))) with K = 2 conjuncts, beta = 0.05; coverage =
  fraction of pilots whose out-of-sample FPR (quantile, eps=0) is below it.
* Validation MAE: |FPR estimated on the held-out last third of the pilot - out-of-sample FPR|.

| Stream | N | quantile eps=0: FPR mean (95th pct) | quantile eps=0.05: FPR | min-of-pilot: FPR | OER (quantile eps=0) | DKW bound | coverage | validation MAE |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| Claude Sonnet 4.5 / TriviaQA | 10 | 0.486 (0.85) | 0.286 | 0.262 | 0.012 | 5.25 | 1.00 | 0.383 |
| Claude Sonnet 4.5 / TriviaQA | 20 | 0.397 (0.53) | 0.170 | 0.158 | 0.012 | 3.74 | 1.00 | 0.315 |
| Claude Sonnet 4.5 / TriviaQA | 40 | 0.340 (0.47) | 0.132 | 0.094 | 0.019 | 2.68 | 1.00 | 0.307 |
| Claude Sonnet 4.5 / TriviaQA | 80 | 0.331 (0.51) | 0.148 | 0.063 | 0.020 | 1.92 | 1.00 | 0.289 |
| Claude Sonnet 4.5 / TriviaQA | 120 | 0.329 (0.49) | 0.120 | 0.044 | 0.024 | 1.59 | 1.00 | 0.242 |
| Claude Sonnet 4.5 / TriviaQA | 160 | 0.312 (0.50) | 0.100 | 0.036 | 0.025 | 1.39 | 1.00 | 0.231 |
| Claude Sonnet 4.5 / TriviaQA | 240 | 0.319 (0.47) | 0.086 | 0.030 | 0.023 | 1.15 | 1.00 | 0.281 |
| Claude Sonnet 4.5 / TriviaQA | 320 | 0.356 (0.49) | 0.117 | 0.029 | 0.022 | 1.01 | 1.00 | 0.318 |
| Claude Sonnet 4.5 / TriviaQA | 480 | 0.194 (0.38) | 0.037 | 0.000 | 0.025 | 0.84 | 1.00 | 0.124 |
| GPT-5 / TriviaQA | 10 | 0.633 (0.88) | 0.366 | 0.354 | 0.012 | 6.72 | 1.00 | 0.428 |
| GPT-5 / TriviaQA | 20 | 0.542 (0.77) | 0.273 | 0.252 | 0.010 | 4.78 | 1.00 | 0.367 |
| GPT-5 / TriviaQA | 40 | 0.413 (0.75) | 0.194 | 0.166 | 0.048 | 3.41 | 1.00 | 0.407 |
| GPT-5 / TriviaQA | 80 | 0.335 (0.90) | 0.138 | 0.103 | 0.079 | 2.44 | 1.00 | 0.380 |
| GPT-5 / TriviaQA | 120 | 0.188 (0.63) | 0.090 | 0.050 | 0.080 | 2.01 | 1.00 | 0.260 |
| GPT-5 / TriviaQA | 160 | 0.146 (0.38) | 0.068 | 0.021 | 0.028 | 1.76 | 1.00 | 0.311 |
| GPT-5 / TriviaQA | 240 | 0.088 (0.21) | 0.056 | 0.011 | 0.027 | 1.45 | 1.00 | 0.373 |
| GPT-5 / TriviaQA | 320 | 0.079 (0.10) | 0.055 | 0.007 | 0.022 | 1.27 | 1.00 | 0.353 |
| GPT-5 / TriviaQA | 480 | 0.056 (0.06) | 0.037 | 0.000 | 0.028 | 1.06 | 1.00 | 0.271 |
| Claude Haiku 4.5 / TriviaQA | 10 | 0.967 (1.00) | 0.894 | 0.888 | 0.000 | 7.29 | 1.00 | 0.389 |
| Claude Haiku 4.5 / TriviaQA | 20 | 0.941 (1.00) | 0.847 | 0.828 | 0.001 | 5.18 | 1.00 | 0.358 |
| Claude Haiku 4.5 / TriviaQA | 40 | 0.790 (1.00) | 0.611 | 0.574 | 0.007 | 3.69 | 1.00 | 0.401 |
| Claude Haiku 4.5 / TriviaQA | 80 | 0.705 (1.00) | 0.597 | 0.533 | 0.007 | 2.64 | 1.00 | 0.543 |
| Claude Haiku 4.5 / TriviaQA | 120 | 0.689 (1.00) | 0.513 | 0.408 | 0.006 | 2.18 | 1.00 | 0.346 |
| Claude Haiku 4.5 / TriviaQA | 160 | 0.567 (0.96) | 0.361 | 0.183 | 0.007 | 1.90 | 1.00 | 0.145 |
| Claude Haiku 4.5 / TriviaQA | 240 | 0.106 (0.11) | 0.056 | 0.000 | 0.008 | 1.57 | 1.00 | 0.006 |
| Qwen3-4B / TriviaQA | 10 | 0.922 (1.00) | 0.820 | 0.807 | 0.000 | 5.19 | 1.00 | 0.096 |
| Qwen3-4B / TriviaQA | 20 | 0.763 (1.00) | 0.676 | 0.661 | 0.011 | 3.70 | 1.00 | 0.204 |
| Qwen3-4B / TriviaQA | 40 | 0.525 (0.92) | 0.379 | 0.334 | 0.225 | 2.65 | 1.00 | 0.270 |
| Qwen3-4B / TriviaQA | 80 | 0.198 (0.47) | 0.109 | 0.087 | 0.603 | 1.90 | 1.00 | 0.474 |
| Qwen3-4B / TriviaQA | 120 | 0.062 (0.26) | 0.000 | 0.000 | 0.841 | 1.57 | 1.00 | 0.623 |
| Qwen3-4B / TriviaQA | 160 | 0.000 (0.00) | 0.000 | 0.000 | 0.995 | 1.37 | 1.00 | 0.790 |
| Qwen3-4B / TriviaQA | 240 | 0.000 (0.00) | 0.000 | 0.000 | 1.000 | 1.14 | 1.00 | 1.000 |
| Qwen3-8B / TriviaQA | 10 | 0.927 (0.99) | 0.851 | 0.844 | 0.000 | 7.14 | 1.00 | 0.130 |
| Qwen3-8B / TriviaQA | 20 | 0.838 (0.98) | 0.745 | 0.719 | 0.006 | 5.08 | 1.00 | 0.208 |
| Qwen3-8B / TriviaQA | 40 | 0.623 (0.92) | 0.398 | 0.356 | 0.174 | 3.62 | 1.00 | 0.286 |
| Qwen3-8B / TriviaQA | 80 | 0.385 (0.83) | 0.173 | 0.138 | 0.449 | 2.59 | 1.00 | 0.398 |
| Qwen3-8B / TriviaQA | 120 | 0.196 (0.82) | 0.037 | 0.020 | 0.660 | 2.13 | 1.00 | 0.452 |
| Qwen3-8B / TriviaQA | 160 | 0.003 (0.03) | 0.000 | 0.000 | 0.931 | 1.86 | 1.00 | 0.500 |
| Qwen3-8B / TriviaQA | 240 | 0.000 (0.00) | 0.000 | 0.000 | 1.000 | 1.54 | 1.00 | 0.944 |
| Qwen2.5-7B / TriviaQA | 10 | 0.927 (0.99) | 0.863 | 0.857 | 0.000 | 6.64 | 1.00 | 0.202 |
| Qwen2.5-7B / TriviaQA | 20 | 0.858 (0.99) | 0.797 | 0.778 | 0.001 | 4.73 | 1.00 | 0.270 |
| Qwen2.5-7B / TriviaQA | 40 | 0.672 (0.99) | 0.508 | 0.470 | 0.131 | 3.37 | 1.00 | 0.251 |
| Qwen2.5-7B / TriviaQA | 80 | 0.390 (0.93) | 0.317 | 0.278 | 0.350 | 2.41 | 1.00 | 0.363 |
| Qwen2.5-7B / TriviaQA | 120 | 0.199 (0.65) | 0.121 | 0.101 | 0.537 | 1.99 | 1.00 | 0.419 |
| Qwen2.5-7B / TriviaQA | 160 | 0.023 (0.15) | 0.000 | 0.000 | 0.753 | 1.74 | 1.00 | 0.439 |
| Qwen2.5-7B / TriviaQA | 240 | 0.000 (0.00) | 0.000 | 0.000 | 1.000 | 1.44 | 1.00 | 0.794 |
| Claude Sonnet 4.5 / MedMCQA | 10 | 0.618 (0.82) | 0.382 | 0.370 | 0.028 | 4.68 | 1.00 | 0.400 |
| Claude Sonnet 4.5 / MedMCQA | 20 | 0.444 (0.86) | 0.238 | 0.217 | 0.047 | 3.34 | 1.00 | 0.446 |
| Claude Sonnet 4.5 / MedMCQA | 40 | 0.280 (0.50) | 0.110 | 0.082 | 0.051 | 2.39 | 1.00 | 0.392 |
| Claude Sonnet 4.5 / MedMCQA | 80 | 0.067 (0.23) | 0.005 | 0.001 | 0.066 | 1.72 | 1.00 | 0.540 |
| Claude Sonnet 4.5 / MedMCQA | 120 | 0.007 (0.01) | 0.006 | 0.000 | 0.059 | 1.42 | 1.00 | 0.497 |
| Claude Sonnet 4.5 / MedMCQA | 160 | 0.004 (0.01) | 0.004 | 0.000 | 0.057 | 1.25 | 1.00 | 0.345 |
| Claude Sonnet 4.5 / MedMCQA | 240 | 0.000 (0.00) | 0.000 | 0.000 | 0.067 | 1.03 | 1.00 | 0.287 |
| GPT-5 / MedMCQA | 10 | 0.718 (0.95) | 0.597 | 0.587 | 0.025 | 5.68 | 1.00 | 0.316 |
| GPT-5 / MedMCQA | 20 | 0.507 (0.74) | 0.329 | 0.312 | 0.047 | 4.05 | 1.00 | 0.362 |
| GPT-5 / MedMCQA | 40 | 0.221 (0.52) | 0.054 | 0.029 | 0.098 | 2.89 | 1.00 | 0.425 |
| GPT-5 / MedMCQA | 80 | 0.033 (0.13) | 0.006 | 0.001 | 0.045 | 2.07 | 1.00 | 0.705 |
| GPT-5 / MedMCQA | 120 | 0.010 (0.02) | 0.005 | 0.000 | 0.049 | 1.71 | 1.00 | 0.417 |
| GPT-5 / MedMCQA | 160 | 0.011 (0.02) | 0.004 | 0.000 | 0.047 | 1.50 | 1.00 | 0.104 |
| GPT-5 / MedMCQA | 240 | 0.006 (0.01) | 0.006 | 0.000 | 0.050 | 1.24 | 1.00 | 0.064 |
| Claude Haiku 4.5 / MedMCQA | 10 | 0.824 (0.92) | 0.729 | 0.718 | 0.014 | 5.27 | 1.00 | 0.142 |
| Claude Haiku 4.5 / MedMCQA | 20 | 0.753 (0.96) | 0.568 | 0.544 | 0.032 | 3.76 | 1.00 | 0.251 |
| Claude Haiku 4.5 / MedMCQA | 40 | 0.470 (0.84) | 0.308 | 0.269 | 0.071 | 2.68 | 1.00 | 0.370 |
| Claude Haiku 4.5 / MedMCQA | 80 | 0.232 (0.28) | 0.152 | 0.091 | 0.113 | 1.93 | 1.00 | 0.504 |
| Claude Haiku 4.5 / MedMCQA | 120 | 0.193 (0.24) | 0.093 | 0.037 | 0.054 | 1.59 | 1.00 | 0.509 |
| Claude Haiku 4.5 / MedMCQA | 160 | 0.165 (0.20) | 0.068 | 0.019 | 0.057 | 1.39 | 1.00 | 0.311 |
| Claude Haiku 4.5 / MedMCQA | 240 | 0.078 (0.08) | 0.056 | 0.000 | 0.058 | 1.16 | 1.00 | 0.268 |
| Qwen3-4B / MedMCQA | 10 | 0.805 (0.98) | 0.724 | 0.710 | 0.029 | 5.54 | 1.00 | 0.117 |
| Qwen3-4B / MedMCQA | 20 | 0.672 (0.84) | 0.506 | 0.480 | 0.077 | 3.95 | 1.00 | 0.264 |
| Qwen3-4B / MedMCQA | 40 | 0.281 (0.59) | 0.125 | 0.098 | 0.277 | 2.82 | 1.00 | 0.414 |
| Qwen3-4B / MedMCQA | 80 | 0.018 (0.06) | 0.000 | 0.000 | 0.682 | 2.02 | 1.00 | 0.722 |
| Qwen3-4B / MedMCQA | 120 | 0.000 (0.00) | 0.000 | 0.000 | 0.922 | 1.67 | 1.00 | 0.731 |
| Qwen3-4B / MedMCQA | 160 | 0.000 (0.00) | 0.000 | 0.000 | 0.992 | 1.46 | 1.00 | 0.520 |
| Qwen3-4B / MedMCQA | 240 | 0.000 (0.00) | 0.000 | 0.000 | 1.000 | 1.21 | 1.00 | 0.175 |
| Qwen3-8B / MedMCQA | 10 | 0.858 (0.96) | 0.757 | 0.751 | 0.000 | 4.74 | 1.00 | 0.131 |
| Qwen3-8B / MedMCQA | 20 | 0.708 (0.87) | 0.613 | 0.597 | 0.043 | 3.38 | 1.00 | 0.233 |
| Qwen3-8B / MedMCQA | 40 | 0.470 (0.67) | 0.329 | 0.311 | 0.216 | 2.42 | 1.00 | 0.332 |
| Qwen3-8B / MedMCQA | 80 | 0.151 (0.34) | 0.042 | 0.027 | 0.566 | 1.74 | 1.00 | 0.396 |
| Qwen3-8B / MedMCQA | 120 | 0.005 (0.03) | 0.000 | 0.000 | 0.901 | 1.44 | 1.00 | 0.518 |
| Qwen3-8B / MedMCQA | 160 | 0.000 (0.00) | 0.000 | 0.000 | 0.971 | 1.26 | 1.00 | 0.419 |
| Qwen3-8B / MedMCQA | 240 | 0.000 (0.00) | 0.000 | 0.000 | 1.000 | 1.05 | 1.00 | 0.000 |
| Qwen2.5-7B / MedMCQA | 10 | 0.807 (0.97) | 0.695 | 0.684 | 0.033 | 5.28 | 1.00 | 0.119 |
| Qwen2.5-7B / MedMCQA | 20 | 0.666 (0.87) | 0.549 | 0.513 | 0.088 | 3.76 | 1.00 | 0.277 |
| Qwen2.5-7B / MedMCQA | 40 | 0.338 (0.76) | 0.187 | 0.161 | 0.316 | 2.69 | 1.00 | 0.412 |
| Qwen2.5-7B / MedMCQA | 80 | 0.029 (0.13) | 0.000 | 0.000 | 0.717 | 1.93 | 1.00 | 0.658 |
| Qwen2.5-7B / MedMCQA | 120 | 0.000 (0.00) | 0.000 | 0.000 | 0.984 | 1.60 | 1.00 | 0.684 |
| Qwen2.5-7B / MedMCQA | 160 | 0.000 (0.00) | 0.000 | 0.000 | 1.000 | 1.40 | 1.00 | 0.484 |
| Qwen2.5-7B / MedMCQA | 240 | 0.000 (0.00) | 0.000 | 0.000 | 1.000 | 1.16 | 1.00 | 0.000 |

## Autocorrelation and the pilot length the bound requires

| Stream | tau_int (steps) | pilot for slack 0.05 | pilot for slack 0.10 |
|---|---:|---:|---:|
| Claude Sonnet 4.5 / TriviaQA | 30.3 | 26536 | 6634 |
| GPT-5 / TriviaQA | 50.1 | 43869 | 10967 |
| Claude Haiku 4.5 / TriviaQA | 59.0 | 51690 | 12923 |
| Qwen3-4B / TriviaQA | 29.6 | 25930 | 6482 |
| Qwen3-8B / TriviaQA | 56.6 | 49571 | 12393 |
| Qwen2.5-7B / TriviaQA | 48.9 | 42822 | 10706 |
| Claude Sonnet 4.5 / MedMCQA | 23.9 | 20978 | 5245 |
| GPT-5 / MedMCQA | 35.5 | 31138 | 7785 |
| Claude Haiku 4.5 / MedMCQA | 30.5 | 26721 | 6680 |
| Qwen3-4B / MedMCQA | 33.8 | 29615 | 7404 |
| Qwen3-8B / MedMCQA | 24.6 | 21550 | 5388 |
| Qwen2.5-7B / MedMCQA | 30.6 | 26841 | 6710 |

![calibration](figures/calibration_real.png)

## Conformal risk control: a finite-sample FPR guarantee that holds on real streams
Calibrate on m honest pilot *sessions* (20 steps each, disjoint items, each from the pre-warmed state).
Thresholds are theta_k = ref_k c (ref_k fixed from the separate 120-item pool); L_j(c) is the fraction of
session j's steps denied. The largest c with (m mean_j L_j(c) + 1)/(m + 1) <= delta guarantees
E[per-step honest FPR of a new session] <= delta for exchangeable sessions, finite-sample and for ANY
dependence inside a session (so the autocorrelation that makes the DKW bound vacuous does not matter).
It needs only m >= 1/delta - 1 sessions. Checked over 50 random splits of the real honest streams.

(A session-level variant that bounds P(an honest session is ever denied) also holds empirically, but forces
the threshold to about zero (OER 0.83-1.00): honest models occasionally produce 8-step windows as badly
calibrated as a sleeper's, so "never deny an honest session" is incompatible with security.)

| Stream | delta | pilot sessions m | splits | honest sessions ever denied | (90th pct) | per-step FPR (guarantee: <= delta) | OER | latency (steps) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Claude Sonnet 4.5 / TriviaQA | 0.05 | 19 | 50 | 0.020 | 0.01 | 0.002 | 0.907 | 36.3 |
| Claude Sonnet 4.5 / TriviaQA | 0.05 | 24 | 50 | 0.112 | 0.24 | 0.013 | 0.400 | 16.0 |
| Claude Sonnet 4.5 / TriviaQA | 0.05 | 29 | 50 | 0.182 | 0.31 | 0.019 | 0.193 | 7.7 |
| Claude Sonnet 4.5 / TriviaQA | 0.05 | 34 | 50 | 0.229 | 0.37 | 0.028 | 0.057 | 2.3 |
| Claude Sonnet 4.5 / TriviaQA | 0.05 | 39 | 50 | 0.260 | 0.50 | 0.034 | 0.050 | 2.0 |
| Claude Sonnet 4.5 / TriviaQA | 0.1 | 9 | 50 | 0.037 | 0.20 | 0.005 | 0.830 | 33.2 |
| Claude Sonnet 4.5 / TriviaQA | 0.1 | 14 | 50 | 0.283 | 0.42 | 0.048 | 0.044 | 1.8 |
| Claude Sonnet 4.5 / TriviaQA | 0.1 | 19 | 50 | 0.338 | 0.50 | 0.062 | 0.037 | 1.5 |
| Claude Sonnet 4.5 / TriviaQA | 0.1 | 24 | 50 | 0.349 | 0.48 | 0.061 | 0.035 | 1.4 |
| Claude Sonnet 4.5 / TriviaQA | 0.1 | 29 | 50 | 0.372 | 0.50 | 0.070 | 0.034 | 1.3 |
| Claude Sonnet 4.5 / TriviaQA | 0.1 | 34 | 50 | 0.384 | 0.55 | 0.079 | 0.031 | 1.2 |
| Claude Sonnet 4.5 / TriviaQA | 0.1 | 39 | 50 | 0.427 | 0.67 | 0.088 | 0.032 | 1.3 |
| GPT-5 / TriviaQA | 0.05 | 19 | 50 | 0.015 | 0.00 | 0.002 | 0.943 | 37.7 |
| GPT-5 / TriviaQA | 0.05 | 24 | 50 | 0.112 | 0.29 | 0.010 | 0.510 | 20.4 |
| GPT-5 / TriviaQA | 0.05 | 29 | 50 | 0.164 | 0.38 | 0.018 | 0.396 | 15.9 |
| GPT-5 / TriviaQA | 0.05 | 34 | 50 | 0.245 | 0.37 | 0.030 | 0.092 | 3.7 |
| GPT-5 / TriviaQA | 0.05 | 39 | 50 | 0.223 | 0.50 | 0.025 | 0.074 | 3.0 |
| GPT-5 / TriviaQA | 0.1 | 9 | 50 | 0.033 | 0.17 | 0.005 | 0.886 | 35.4 |
| GPT-5 / TriviaQA | 0.1 | 14 | 50 | 0.289 | 0.42 | 0.039 | 0.047 | 1.9 |
| GPT-5 / TriviaQA | 0.1 | 19 | 50 | 0.391 | 0.54 | 0.066 | 0.035 | 1.4 |
| GPT-5 / TriviaQA | 0.1 | 24 | 50 | 0.412 | 0.58 | 0.067 | 0.032 | 1.3 |
| GPT-5 / TriviaQA | 0.1 | 29 | 50 | 0.421 | 0.57 | 0.074 | 0.032 | 1.3 |
| GPT-5 / TriviaQA | 0.1 | 34 | 50 | 0.467 | 0.64 | 0.083 | 0.029 | 1.2 |
| GPT-5 / TriviaQA | 0.1 | 39 | 50 | 0.423 | 0.67 | 0.079 | 0.030 | 1.2 |
| Claude Haiku 4.5 / TriviaQA | 0.1 | 9 | 50 | 0.010 | 0.00 | 0.002 | 0.982 | 39.3 |
| Qwen3-4B / TriviaQA | 0.1 | 9 | 50 | 0.000 | 0.00 | 0.000 | 1.000 | 40.0 |
| Qwen3-8B / TriviaQA | 0.1 | 9 | 50 | 0.000 | 0.00 | 0.000 | 1.000 | 40.0 |
| Qwen2.5-7B / TriviaQA | 0.1 | 9 | 50 | 0.000 | 0.00 | 0.000 | 1.000 | 40.0 |
| Claude Sonnet 4.5 / MedMCQA | 0.1 | 9 | 50 | 0.020 | 0.00 | 0.002 | 0.963 | 38.5 |
| GPT-5 / MedMCQA | 0.1 | 9 | 50 | 0.000 | 0.00 | 0.000 | 1.000 | 40.0 |
| Claude Haiku 4.5 / MedMCQA | 0.1 | 9 | 50 | 0.000 | 0.00 | 0.000 | 1.000 | 40.0 |
| Qwen3-4B / MedMCQA | 0.1 | 9 | 50 | 0.000 | 0.00 | 0.000 | 1.000 | 40.0 |
| Qwen3-8B / MedMCQA | 0.1 | 9 | 50 | 0.000 | 0.00 | 0.000 | 1.000 | 40.0 |
| Qwen2.5-7B / MedMCQA | 0.1 | 9 | 50 | 0.000 | 0.00 | 0.000 | 1.000 | 40.0 |

## TGCC-R: conformal risk control on deployment sessions (the revised method)
Window selected from the honest pilot; a conjunct on every layer; CRC over the two-stage nested family on m honest
10-step sessions drawn from the deployment workload (the pilot is only the reference pool). Guarantee:
E[per-step honest FPR] <= delta. 50 random splits.

| Stream | window | delta | sessions m | splits | per-step FPR (mean) | (90th pct) | sleeper OER | off-topic OER |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Claude Sonnet 4.5 / TriviaQA | 4 | 0.1 | 9 | 50 | 0.011 | 0.05 | 0.765 | 0.160 |
| Claude Sonnet 4.5 / TriviaQA | 4 | 0.1 | 14 | 50 | 0.035 | 0.09 | 0.356 | 0.000 |
| Claude Sonnet 4.5 / TriviaQA | 4 | 0.1 | 19 | 50 | 0.052 | 0.09 | 0.138 | 0.000 |
| Claude Sonnet 4.5 / TriviaQA | 4 | 0.1 | 24 | 50 | 0.062 | 0.09 | 0.019 | 0.000 |
| Claude Sonnet 4.5 / TriviaQA | 4 | 0.1 | 29 | 50 | 0.067 | 0.10 | 0.038 | 0.000 |
| Claude Sonnet 4.5 / TriviaQA | 4 | 0.1 | 39 | 50 | 0.071 | 0.10 | 0.019 | 0.000 |
| Claude Sonnet 4.5 / TriviaQA | 4 | 0.2 | 9 | 50 | 0.081 | 0.10 | 0.037 | 0.000 |
| Claude Sonnet 4.5 / TriviaQA | 4 | 0.2 | 14 | 50 | 0.090 | 0.11 | 0.017 | 0.000 |
| Claude Sonnet 4.5 / TriviaQA | 4 | 0.2 | 19 | 50 | 0.088 | 0.11 | 0.017 | 0.000 |
| Claude Sonnet 4.5 / TriviaQA | 4 | 0.2 | 24 | 50 | 0.088 | 0.10 | 0.017 | 0.000 |
| Claude Sonnet 4.5 / TriviaQA | 4 | 0.2 | 29 | 50 | 0.090 | 0.11 | 0.017 | 0.000 |
| Claude Sonnet 4.5 / TriviaQA | 4 | 0.2 | 39 | 50 | 0.088 | 0.11 | 0.018 | 0.000 |
| GPT-5 / TriviaQA | 4 | 0.1 | 9 | 50 | 0.008 | 0.04 | 0.843 | 0.000 |
| GPT-5 / TriviaQA | 4 | 0.1 | 14 | 50 | 0.032 | 0.08 | 0.510 | 0.000 |
| GPT-5 / TriviaQA | 4 | 0.1 | 19 | 50 | 0.055 | 0.10 | 0.176 | 0.000 |
| GPT-5 / TriviaQA | 4 | 0.1 | 24 | 50 | 0.064 | 0.10 | 0.037 | 0.000 |
| GPT-5 / TriviaQA | 4 | 0.1 | 29 | 50 | 0.069 | 0.11 | 0.037 | 0.000 |
| GPT-5 / TriviaQA | 4 | 0.1 | 39 | 50 | 0.080 | 0.13 | 0.016 | 0.000 |
| GPT-5 / TriviaQA | 4 | 0.2 | 9 | 50 | 0.098 | 0.12 | 0.015 | 0.000 |
| GPT-5 / TriviaQA | 4 | 0.2 | 14 | 50 | 0.108 | 0.14 | 0.015 | 0.000 |
| GPT-5 / TriviaQA | 4 | 0.2 | 19 | 50 | 0.112 | 0.14 | 0.015 | 0.000 |
| GPT-5 / TriviaQA | 4 | 0.2 | 24 | 50 | 0.112 | 0.13 | 0.014 | 0.000 |
| GPT-5 / TriviaQA | 4 | 0.2 | 29 | 50 | 0.109 | 0.13 | 0.013 | 0.000 |
| GPT-5 / TriviaQA | 4 | 0.2 | 39 | 50 | 0.112 | 0.14 | 0.013 | 0.000 |
| Claude Haiku 4.5 / TriviaQA | 4 | 0.1 | 9 | 50 | 0.000 | 0.00 | 0.993 | 0.000 |
| Claude Haiku 4.5 / TriviaQA | 4 | 0.1 | 14 | 50 | 0.008 | 0.00 | 0.915 | 0.000 |
| Claude Haiku 4.5 / TriviaQA | 4 | 0.1 | 19 | 50 | 0.007 | 0.00 | 0.935 | 0.000 |
| Claude Haiku 4.5 / TriviaQA | 4 | 0.2 | 9 | 50 | 0.096 | 0.20 | 0.310 | 0.000 |
| Claude Haiku 4.5 / TriviaQA | 4 | 0.2 | 14 | 50 | 0.142 | 0.24 | 0.053 | 0.000 |
| Claude Haiku 4.5 / TriviaQA | 4 | 0.2 | 19 | 50 | 0.157 | 0.27 | 0.032 | 0.000 |
| Qwen3-4B / TriviaQA | 24 | 0.1 | 9 | 50 | 0.003 | 0.00 | 0.963 | 0.280 |
| Qwen3-4B / TriviaQA | 24 | 0.1 | 14 | 50 | 0.003 | 0.01 | 0.941 | 0.000 |
| Qwen3-4B / TriviaQA | 24 | 0.1 | 19 | 50 | 0.004 | 0.01 | 0.933 | 0.000 |
| Qwen3-4B / TriviaQA | 24 | 0.2 | 9 | 50 | 0.003 | 0.00 | 0.945 | 0.000 |
| Qwen3-4B / TriviaQA | 24 | 0.2 | 14 | 50 | 0.003 | 0.01 | 0.941 | 0.000 |
| Qwen3-4B / TriviaQA | 24 | 0.2 | 19 | 50 | 0.004 | 0.01 | 0.933 | 0.000 |
| Qwen3-8B / TriviaQA | 24 | 0.1 | 9 | 50 | 0.003 | 0.00 | 0.693 | 0.000 |
| Qwen3-8B / TriviaQA | 24 | 0.1 | 14 | 50 | 0.003 | 0.01 | 0.573 | 0.000 |
| Qwen3-8B / TriviaQA | 24 | 0.1 | 19 | 50 | 0.004 | 0.01 | 0.551 | 0.000 |
| Qwen3-8B / TriviaQA | 24 | 0.2 | 9 | 50 | 0.003 | 0.00 | 0.561 | 0.000 |
| Qwen3-8B / TriviaQA | 24 | 0.2 | 14 | 50 | 0.003 | 0.01 | 0.573 | 0.000 |
| Qwen3-8B / TriviaQA | 24 | 0.2 | 19 | 50 | 0.004 | 0.01 | 0.551 | 0.000 |
| Qwen2.5-7B / TriviaQA | 24 | 0.1 | 9 | 50 | 0.000 | 0.00 | 0.307 | 0.000 |
| Qwen2.5-7B / TriviaQA | 24 | 0.1 | 14 | 50 | 0.000 | 0.00 | 0.305 | 0.000 |
| Qwen2.5-7B / TriviaQA | 24 | 0.1 | 19 | 50 | 0.000 | 0.00 | 0.305 | 0.000 |
| Qwen2.5-7B / TriviaQA | 24 | 0.2 | 9 | 50 | 0.000 | 0.00 | 0.307 | 0.000 |
| Qwen2.5-7B / TriviaQA | 24 | 0.2 | 14 | 50 | 0.000 | 0.00 | 0.305 | 0.000 |
| Qwen2.5-7B / TriviaQA | 24 | 0.2 | 19 | 50 | 0.000 | 0.00 | 0.305 | 0.000 |
| Claude Sonnet 4.5 / MedMCQA | 16 | 0.1 | 9 | 50 | 0.000 | 0.00 | 1.000 | 0.000 |
| Claude Sonnet 4.5 / MedMCQA | 16 | 0.1 | 14 | 50 | 0.032 | 0.10 | 0.627 | 0.000 |
| Claude Sonnet 4.5 / MedMCQA | 16 | 0.1 | 19 | 50 | 0.051 | 0.12 | 0.414 | 0.000 |
| Claude Sonnet 4.5 / MedMCQA | 16 | 0.2 | 9 | 50 | 0.085 | 0.13 | 0.160 | 0.000 |
| Claude Sonnet 4.5 / MedMCQA | 16 | 0.2 | 14 | 50 | 0.093 | 0.14 | 0.099 | 0.000 |
| Claude Sonnet 4.5 / MedMCQA | 16 | 0.2 | 19 | 50 | 0.099 | 0.16 | 0.103 | 0.000 |
| GPT-5 / MedMCQA | 16 | 0.1 | 9 | 50 | 0.006 | 0.00 | 0.928 | 0.000 |
| GPT-5 / MedMCQA | 16 | 0.1 | 14 | 50 | 0.041 | 0.08 | 0.315 | 0.000 |
| GPT-5 / MedMCQA | 16 | 0.1 | 19 | 50 | 0.052 | 0.11 | 0.207 | 0.000 |
| GPT-5 / MedMCQA | 16 | 0.2 | 9 | 50 | 0.063 | 0.10 | 0.113 | 0.000 |
| GPT-5 / MedMCQA | 16 | 0.2 | 14 | 50 | 0.062 | 0.09 | 0.083 | 0.000 |
| GPT-5 / MedMCQA | 16 | 0.2 | 19 | 50 | 0.070 | 0.12 | 0.090 | 0.000 |
| Claude Haiku 4.5 / MedMCQA | 12 | 0.1 | 9 | 50 | 0.002 | 0.00 | 0.982 | 0.000 |
| Claude Haiku 4.5 / MedMCQA | 12 | 0.1 | 14 | 50 | 0.021 | 0.12 | 0.851 | 0.000 |
| Claude Haiku 4.5 / MedMCQA | 12 | 0.1 | 19 | 50 | 0.027 | 0.13 | 0.828 | 0.000 |
| Claude Haiku 4.5 / MedMCQA | 12 | 0.2 | 9 | 50 | 0.112 | 0.19 | 0.195 | 0.000 |
| Claude Haiku 4.5 / MedMCQA | 12 | 0.2 | 14 | 50 | 0.136 | 0.20 | 0.076 | 0.000 |
| Claude Haiku 4.5 / MedMCQA | 12 | 0.2 | 19 | 50 | 0.150 | 0.24 | 0.055 | 0.000 |
| Qwen3-4B / MedMCQA | 24 | 0.1 | 9 | 50 | 0.000 | 0.00 | 1.000 | 0.000 |
| Qwen3-4B / MedMCQA | 24 | 0.1 | 14 | 50 | 0.000 | 0.00 | 1.000 | 0.000 |
| Qwen3-4B / MedMCQA | 24 | 0.1 | 19 | 50 | 0.000 | 0.00 | 1.000 | 0.000 |
| Qwen3-4B / MedMCQA | 24 | 0.2 | 9 | 50 | 0.000 | 0.00 | 1.000 | 0.000 |
| Qwen3-4B / MedMCQA | 24 | 0.2 | 14 | 50 | 0.000 | 0.00 | 1.000 | 0.000 |
| Qwen3-4B / MedMCQA | 24 | 0.2 | 19 | 50 | 0.000 | 0.00 | 1.000 | 0.000 |
| Qwen3-8B / MedMCQA | 24 | 0.1 | 9 | 50 | 0.000 | 0.00 | 0.999 | 0.000 |
| Qwen3-8B / MedMCQA | 24 | 0.1 | 14 | 50 | 0.000 | 0.00 | 0.998 | 0.000 |
| Qwen3-8B / MedMCQA | 24 | 0.1 | 19 | 50 | 0.000 | 0.00 | 0.998 | 0.000 |
| Qwen3-8B / MedMCQA | 24 | 0.2 | 9 | 50 | 0.000 | 0.00 | 0.999 | 0.000 |
| Qwen3-8B / MedMCQA | 24 | 0.2 | 14 | 50 | 0.000 | 0.00 | 0.998 | 0.000 |
| Qwen3-8B / MedMCQA | 24 | 0.2 | 19 | 50 | 0.000 | 0.00 | 0.998 | 0.000 |
| Qwen2.5-7B / MedMCQA | 24 | 0.1 | 9 | 50 | 0.000 | 0.00 | 1.000 | 0.000 |
| Qwen2.5-7B / MedMCQA | 24 | 0.1 | 14 | 50 | 0.000 | 0.00 | 1.000 | 0.000 |
| Qwen2.5-7B / MedMCQA | 24 | 0.1 | 19 | 50 | 0.000 | 0.00 | 1.000 | 0.000 |
| Qwen2.5-7B / MedMCQA | 24 | 0.2 | 9 | 50 | 0.000 | 0.00 | 1.000 | 0.000 |
| Qwen2.5-7B / MedMCQA | 24 | 0.2 | 14 | 50 | 0.000 | 0.00 | 1.000 | 0.000 |
| Qwen2.5-7B / MedMCQA | 24 | 0.2 | 19 | 50 | 0.000 | 0.00 | 1.000 | 0.000 |
