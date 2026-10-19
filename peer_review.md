# Peer Reviews — Submission1175

---

## Official Review of Submission1175 by Reviewer 14qA

Official Reviewby Reviewer 14qA16 Sept 2026, 17:10 (modified: 27 Sept 2026, 20:34)Program Chairs, Senior Area Chairs, Area Chairs, Reviewers Submitted, Reviewer 14qA, Authors[Revisions](https://openreview.net/revisions?id=GHDR7qINom)

**Paper Summary:** The paper argues that layered trust models for multi-agent LLM systems are descriptive taxonomies that do not specify how layers compose, how layer importance adapts, or how trust governs permissions. It proposes: a cross-layer synergy operator using a lower-triangular coupling matrix so a prerequisite-layer deficit discounts dependent layers; a generalized power-mean composite trust with a closed-form conservative fixed point; multiplicative-weights estimation of layer importance grounded in observed failures, claimed no-regret and geometrically convergent; and TGCC, which issues short-lived revocable capability grants conditioned on composite trust and per-prerequisite-layer thresholds. Theorems claim the paradox is broken, revocation latency is logarithmic, and honest false positives decay exponentially.

**Paper Strengths:**

1. The motivating scenario is well chosen
2. Lifting trust from a scalar to a coupled vector is the correct structural response to that diagnosis, and the paper is specific about how it differs from the closest prior work: the TVP paper's defenses tune thresholds and rate limits around a scalar trust signal rather than reshaping how the signal is computed.

**Paper Weaknesses:**

1. The naive baseline has the lowest over-exposure rate in the Table 1.
2. The experiments are far too small for the claims. E1 is 60 factual questions with 2 agents and a single compromise point at step 20. E2 varies team size over {1, 3, 5} with 2 debate rounds. E4 is 20 commits, and the abstract's "blocks 95% of harmful commits" is 19 of 20, where one commit moves the headline to 90% or 100%. E3 and E5 are simulations drawing Bernoulli check signals from latent reliabilities, meaning the trust signals are synthesized rather than measured, so they test the controller's arithmetic rather than whether real LLM check signals behave as assumed.
3. Parameters are numerous, hand-set, and unexplained. Coupling matrix from Appendix B, forgetting factor 0.985, failure penalty 3, power-mean order -6, Hedge learning rate 0.5, coupling strength c = 0.35. The operating region p = -6, c = 0.35 is identified by E3, which is a simulation with synthesized Bernoulli signals. So the parameters that govern the real-LLM experiments were selected on synthetic data, and the paper does not report sensitivity on the real-LLM streams.

**Resubmission:** N/A

**Questions And Suggestions For Rebuttal:**

1. Table 1 reports Naive at OER 0.12 against TGCC's 0.17 on the same experiment, with lower being better. Please explain this. If the rows use different denominators or windows, state them; if OER is not the primary metric, say what is. As printed, the proposed controller is worse than the baseline it is meant to replace on the paper's own headline metric.
2. Definition 1 is not satisfiable by any controller gating on a minimum over layers. Is Theorem 3 stronger than that observation? If so, please state what an adversary could do to a min-aggregator that Definition 1 rules out.
3. The operating region p = -6, c = 0.35 was selected on simulations with synthesized Bernoulli signals. Report parameter sensitivity on the real-LLM streams.

**Relevance:** 3: Moderate - The work is somewhat relevant to the Research track of KDD and is of narrow interest to a sub-community

**Novelty:** 3: Moderate - The paper introduces a new and interesting idea or approach that adds value to the field. The contribution is original and represents an advancement of existing knowledge, demonstrating solid innovation and creativity.

**Technical Quality:** 2: Low - The paper has several technical weaknesses, such as minor methodological flaws, insufficient analysis, or unsupported conclusions. While the work shows some level of competence, it lacks thoroughness and precision. Improvements are necessary for it to be considered robust.

**Presentation:** 2: Low - The paper has noticeable issues with clarity and coherence. The writing may contain several grammatical and typographical errors. Figures and tables are present but may not be well-integrated or effectively used. The presentation allows for understanding but requires effort from the reader.

**Reproducibility:** 3: Moderate - The paper provides a clear and detailed description of the methods, data, and procedures used. Supplementary materials, such as datasets and code, are available and sufficiently documented. Reproducing the results would be feasible with the provided information, though some effort may still be required.

**Reviewer Confidence:** 2: Low - The reviewer has some knowledge of the subject area and is somewhat familiar with the research methods and context of the paper. They understand the main points but may lack depth in certain areas. The reviewer is reasonably confident in their assessment but acknowledges some limitations in their expertise.

**Ethics Review Flag:** No

**Ethics Review Description:** N/A

---

## Official Review of Submission1175 by Reviewer D1aZ

Official Reviewby Reviewer D1aZ16 Sept 2026, 13:34 (modified: 27 Sept 2026, 20:34)Program Chairs, Senior Area Chairs, Area Chairs, Reviewers Submitted, Reviewer D1aZ, Authors[Revisions](https://openreview.net/revisions?id=ExVnxABgfg)

**Paper Summary:** This paper introduces a security framework designed to prevent adversarial exploitation in multi-agent large language model collectives. It addresses the Trust–Vulnerability Paradox (TVP) by operationalizing a five-layer trust stack linked through a lower-triangular coupling matrix and power-mean composite trust model.

**Paper Strengths:**

- The problem framing is interesting. The gap between naming the dimensions of trust and specifying the runtime rule that decides what an agent may do is real, and the three sub-questions the paper poses (composition, weighting, actuation) map cleanly onto its four components. Tying the actuation step to capability-based security and zero-trust architecture rather than inventing a new authorization notion appears to be the right choice.
- The design is coherent, and the mechanism behaves as the intuition suggests. Making the epistemic layer a universal prerequisite, discounting dependants by prerequisite deficits, and then aggregating with a strongly negative power mean is a sensible way to make what the paper calls "an epistemically broken but behaviourally polished agent" visible to a gate.
- Two production providers, bootstrap confidence intervals with a stratified resampling scheme (E6), an indirect prompt-injection probe (E8), a 5000-step drift study (E10), a parameter sensitivity study (E11), and an anonymized artifact repository together suggest genuine effort at falsification rather than demonstration.
- Observing that composite trust occupies a lower numerical range under real-LLM signals than in simulation, and therefore treating threshold selection as a pilot-phase data-driven step rather than transplanting a constant, seems like a lesson many deployment papers omit.

**Paper Weaknesses:**

- The real-LLM evidence rests on a 60-question single-activation episode (E1), a 35-task code pipeline (E4), and a 20-question three-persona probe (E7), each with a small number of seeds. The bootstrap in E6 quantifies within-episode variability but resamples a single episode's signal streams, so it cannot address across-episode or across-task variability. Additional independent episodes, even at the same length, would be more informative than more resamples of one.
- E9 suggests the multi-layer construction may not be necessary for the reported effect. Table 12 shows that holding the epistemic signal high restores OER to 1.00, while holding any other layer high leaves OER at the baseline, and the accompanying text concludes that "the epistemic layer carries the detection load". Read together with the near-minimum aggregation, TGCC's protective behaviour in these experiments appears close to a single rule, namely revoke when an independent critic says the agent is wrong. That is a legitimate and defensible design, but it is a much smaller claim than a five-layer compositional trust calculus, and the paper's framing does not currently reflect it.
- The epistemic probe assumes the availability of the component that is hardest to obtain. The check requires an independent critic that can verify correctness, and the experiments supply one by using factual questions with known answers. In the motivating clinical scenario, an oracle that can adjudicate whether a synthesis is clinically correct is exactly what is unavailable, and if it were available the write could be gated on it directly. Assumption 1 states that the adversary "cannot forge the check signals of layers it does not control", but the epistemic signal is derived from the adversary's own outputs, and E9 shows what happens when it can be influenced. A discussion of critic reliability, and ideally an experiment with a noisy or imperfectly informed critic, would test the framework where it is most likely to fail.
- The math part of this paper may need some double check. For example, the exponential false-positive claim does not appear to follow from Eq. (12). The bound is L exp(-2 (T*_l - theta_c,l)^2 n_l(t)) with n_l(t) = (1 - gamma^t) / (1 - gamma). That effective sample count is bounded above by 1 / (1 - gamma), which the paper itself proves as Proposition 10 and which equals roughly 66.7 at gamma = 0.985. The bound therefore converges geometrically to a strictly positive limit, L exp(-2 Delta^2 / (1 - gamma)), rather than decaying to zero. Section 6.3 even opens by noting that the effective sample count "grows toward a finite ceiling set by the forgetting factor", and then states that the bound "decays to zero exponentially" as the step count grows. The stronger reading appears in the abstract ("decays exponentially with interaction length"), the contributions list, the Key insight box, and the conclusion, so the correction may affect the paper's claims rather than only its wording. Restating the result as geometric convergence to an explicit positive limit would still be a useful theorem.
- Also, Eq. (14) appears ill-posed as printed. Detection requires the compromised layer's trust to fall below theta_c / kappa, which means T*_k < theta_c / kappa < T_k(t_0). Under those inequalities the numerator T_k(t_0) - theta_c / kappa is positive and the denominator T*_k - theta_c / kappa is negative, so the logarithm's argument is negative. Solving the geometric trajectory T(t) = T* + (T(t_0) - T*) gamma^{t - t_0} for the crossing time gives ln[(T_k(t_0) - T*_k) / (theta_c / kappa - T*_k)] divided by ln(1 / gamma), which is presumably the intended expression.
- It is suggested that the authors may provide the code & data for verification and reproducibility.

**Resubmission:** n/a

**Questions And Suggestions For Rebuttal:**

- What is the correct value for E1 Naive over-exposure in Table 1? Table 9, the Figure 1 caption, and the step arithmetic (40 post-compromise steps) all appear to point to 1.00.
- Which of 0.17 (Table 1), 0.11 (Table 9), and 0.25 (Table 12) is TGCC's E1 over-exposure rate on Claude, and what accounts for the differences? The reported 4.2x factor depends on this.
- Given p = -6, a universal epistemic prerequisite in the coupling matrix, and an epistemic prerequisite attached to the E1 capability, why does removing the coupling change revocation latency from 7 steps to 29? Could you show the composite trajectory and the per-layer condition for both settings?

**Relevance:** 3: Moderate - The work is somewhat relevant to the Research track of KDD and is of narrow interest to a sub-community

**Novelty:** 3: Moderate - The paper introduces a new and interesting idea or approach that adds value to the field. The contribution is original and represents an advancement of existing knowledge, demonstrating solid innovation and creativity.

**Technical Quality:** 3: Moderate - The paper demonstrates solid technical quality with a sound methodology and thorough analysis. The results are reliable and well-supported. There may be minor issues, but they do not significantly undermine the overall quality. The work is competently executed and meets acceptable standards.

**Presentation:** 3: Moderate - The paper is organized and generally clear. The writing is mostly free of grammatical and typographical errors, making it easy to read. Figures and tables are effectively used to support the text. The presentation facilitates understanding and conveys the key points effectively.

**Reproducibility:** 3: Moderate - The paper provides a clear and detailed description of the methods, data, and procedures used. Supplementary materials, such as datasets and code, are available and sufficiently documented. Reproducing the results would be feasible with the provided information, though some effort may still be required.

**Reviewer Confidence:** 3: Moderate - The reviewer has a good understanding of the subject area and is familiar with the research methods and context of the paper. They feel confident in their ability to accurately assess the quality and significance of the work. Their evaluation is based on a solid grasp of the content and context.

**Ethics Review Flag:** No

**Ethics Review Description:** N/A

---

## Official Review of Submission1175 by Reviewer RRLq

Official Reviewby Reviewer RRLq15 Sept 2026, 13:39 (modified: 27 Sept 2026, 20:34)Program Chairs, Senior Area Chairs, Area Chairs, Reviewers Submitted, Reviewer RRLq, Authors[Revisions](https://openreview.net/revisions?id=mRbFiwZuOC)

**Paper Summary:** This paper proposes Trust-Gated Capability Control TGCC) for multi-agent LLM systems. It maintains a five-layer trust vector for each agent, propagates failures across dependent trust layers, aggregates them with a negative-order power mean, and dynamically grants or revokes capabilities based on the resulting trust. The paper provides theoretical analysis and evaluates the framework with real LLMs and simulations.

**Paper Strengths:**

1. The paper studies a meaningful problem in multi-agent LLM systems, where an agent may remain cooperative in behavior while becoming unreliable in another trust dimension.
2. The motivation around the Trust Vulnerability Paradox is clear. The proposed framework provides a structured way to combine layered trust and dynamically control agent capabilities.
3. The experiments cover several tasks and include both real LLMs and simulation, giving reasonably broad validation

**Paper Weaknesses:**

1. The reliability of the five underlying trust signals is not sufficiently validated. Some signals rely on LLM-based critics or evaluators, while the role, social, and institutional layers use heuristic or rule-based probes. The paper does not provide sufficient evaluation of the accuracy or stability of these signal estimators, which is important because the effectiveness of TGCC directly depends on their quality.
2. The reported efficiency results do not appear to include the cost of obtaining the trust signals. In the real-LLM setting, some signals require additional LLM-based critics, whereas the reported 10.8 μs per-agent overhead measures only the lightweight controller computation after these signals are available. End-to-end latency and API/token overhead are therefore unclear.
3. The technical novelty of individual components is somewhat limited. Beta reputation updates, multiplicative weighting, power-mean aggregation, and capability-based access control are established techniques, so much of the contribution comes from integrating them into a unified framework.
4. The trust hierarchy and cross-layer dependencies are largely predefined, including the ordering of the five trust layers and the coupling matrix. It is unclear how these dependencies should be determined for different tasks or multi-agent systems, or how sensitive the method is to an incorrectly specified trust structure.
5. The overall organization of the paper could be improved. The manuscript is divided into an unusually large number of sections and subsections, which makes the presentation somewhat fragmented and affects the overall reading flow.

**Resubmission:** No

**Questions And Suggestions For Rebuttal:** See Weaknesses.

**Relevance:** 2: Low - The connection to KDD is weak

**Novelty:** 2: Low - The ideas are relatively minor and largely incremental. The work builds heavily on existing research.

**Technical Quality:** 2: Low - The paper has several technical weaknesses, such as minor methodological flaws, insufficient analysis, or unsupported conclusions. While the work shows some level of competence, it lacks thoroughness and precision. Improvements are necessary for it to be considered robust.

**Presentation:** 2: Low - The paper has noticeable issues with clarity and coherence. The writing may contain several grammatical and typographical errors. Figures and tables are present but may not be well-integrated or effectively used. The presentation allows for understanding but requires effort from the reader.

**Reproducibility:** 3: Moderate - The paper provides a clear and detailed description of the methods, data, and procedures used. Supplementary materials, such as datasets and code, are available and sufficiently documented. Reproducing the results would be feasible with the provided information, though some effort may still be required.

**Reviewer Confidence:** 3: Moderate - The reviewer has a good understanding of the subject area and is familiar with the research methods and context of the paper. They feel confident in their ability to accurately assess the quality and significance of the work. Their evaluation is based on a solid grasp of the content and context.

**Ethics Review Flag:** No

**Ethics Review Description:** N/A

---

## Official Review of Submission1175 by Reviewer eY9w

Official Reviewby Reviewer eY9w14 Sept 2026, 09:37 (modified: 27 Sept 2026, 20:34)Program Chairs, Senior Area Chairs, Area Chairs, Reviewers Submitted, Reviewer eY9w, Authors[Revisions](https://openreview.net/revisions?id=AWzmeMcS3l)

**Paper Summary:** This paper presents a study on trust-gated capability control in the setting of breaking the trust–vulnerability paradox in multi-agent LLM systems. Specifically, the authors design a cross-layersynergy operator that encodes layer dependencies through a lower-triangular coupling matrix, and a generalized power-mean composite trust that admits a closed-form conservative ffxed point and provable bounds. Furthermore, the authors prove that failure-grounded multiplicative-weights estimation of layer importance converges geometrically and is no-regret, and propose Trust-Gated Capability Control (TGCC). TGCC is evaluated by conducting five experiments.

**Paper Strengths:**

1. The authors have formalized the multi-agent trust-gating problem and the Trust-Vulnerability Paradox as a precise property of authorization policies.
2. The authors have designed a cross-layer synergy operator and a generalizedpower-mean composite trust.
3. The authors hava proposed the TGCC algorithm and prove that it has constantper-step overhead.

**Paper Weaknesses:**

1. The writing of this paper needs significant improvements, i.e., the paper in its current form makes it very difficult for readers to understand the technical contributions, given the very long abstract and the very complex organization of the contents .
2. The experimental studies do not involve comparing TGCC with baseline methods, i.e., comparing TGCC with TGCC-NoSyn and Naive can only be considered as an ablation study.
3. Section 9 lacks sensitivity analyses of those important hyperparameters such as forgetting factor, failure penalty, power-mean order and Hedge learning rate.
4. There is not a clear conclusion drawn from the experimental results and the theoretical proofs.

**Resubmission:** This paper is not a Resubmission.

**Questions And Suggestions For Rebuttal:** Please address the points mentioned in the weaknesses.

**Relevance:** 2: Low - The connection to KDD is weak

**Novelty:** 2: Low - The ideas are relatively minor and largely incremental. The work builds heavily on existing research.

**Technical Quality:** 1: Poor - The paper has significant technical errors, methodological flaws, or incorrect conclusions. The work lacks rigor, and the results are unreliable. The overall quality is below acceptable standards, and the technical execution is weak.

**Presentation:** 1: Poor - The paper is poorly organized and difficult to follow. The writing is unclear, with numerous grammatical and typographical errors. Figures and tables, if present, are poorly designed or hard to understand. Overall, the presentation detracts significantly from the readability and comprehension of the work.

**Reproducibility:** 1: Poor - The paper provides insufficient details about the methods, data, and procedures used. There are no available supplementary materials, and the description is so vague that reproducing the results would be extremely difficult or impossible.

**Reviewer Confidence:** 3: Moderate - The reviewer has a good understanding of the subject area and is familiar with the research methods and context of the paper. They feel confident in their ability to accurately assess the quality and significance of the work. Their evaluation is based on a solid grasp of the content and context.

**Ethics Review Flag:** No

**Ethics Review Description:** N/A

---

## Official Review of Submission1175 by Reviewer Jqqf

Official Reviewby Reviewer Jqqf09 Sept 2026, 20:09 (modified: 27 Sept 2026, 20:34)Program Chairs, Senior Area Chairs, Area Chairs, Reviewers Submitted, Reviewer Jqqf, Authors[Revisions](https://openreview.net/revisions?id=rmtub2z332)

**Paper Summary:** This paper proposes Trust-Gated Capability Control (TGCC), which uses five connected trust layers to decide whether an LLM agent should retain its permissions. It combines trust updates, cross-layer coupling, adaptive weights, and capability thresholds. Experiments cover factual questions, multi-agent debate, code generation, and additional robustness scenarios. The paper also claims theoretical guarantees on revocation latency, false positives, and threshold calibration.

**Paper Strengths:**

- Addresses a practical security problem: an agent can appear cooperative while producing incorrect or harmful outputs.
- Connects trust assessment to concrete permission decisions, including revocation, recovery, and audit records.
- Includes experiments across several tasks and examines failure cases such as collusion and unreliable check signals

**Paper Weaknesses:**

1. **Core theoretical guarantees need substantial clarification or correction.** The false-positive result in Theorem 4 appears incompatible with a bounded effective sample count, and Eq. (14) is not well-defined in the stated threshold-crossing regime. These issues affect the claimed guarantees on safety and revocation.
2. **The practical value of the full framework is not sufficiently isolated.** The calibration procedure appears to have a counterintuitive update direction, and Appendix H suggests that detection is dominated by the epistemic checker. Comparisons with epistemic-only or verifier-based gating at matched honest-agent admission rates are needed.
3. **Some experimental claims require reconciliation.** Naive's E1 OER differs between the main text and appendix, while the claimed superiority over all baselines conflicts with the reported AgentGuard OER. The paper should clarify settings, metrics, and whether comparisons are directly comparable.
4. **Presentation could be improved.** The paper introduces many layers, parameters, propositions, and experiments in a short space. Several central assumptions and dependencies between trust signals are difficult to follow, and inconsistencies between the main text and appendix further reduce clarity.

**Resubmission:** Not applicable. This paper is not marked as a resubmission.

**Questions And Suggestions For Rebuttal:** Please address the concerns raised in the weaknesses.

**Relevance:** 3: Moderate - The work is somewhat relevant to the Research track of KDD and is of narrow interest to a sub-community

**Novelty:** 2: Low - The ideas are relatively minor and largely incremental. The work builds heavily on existing research.

**Technical Quality:** 2: Low - The paper has several technical weaknesses, such as minor methodological flaws, insufficient analysis, or unsupported conclusions. While the work shows some level of competence, it lacks thoroughness and precision. Improvements are necessary for it to be considered robust.

**Presentation:** 2: Low - The paper has noticeable issues with clarity and coherence. The writing may contain several grammatical and typographical errors. Figures and tables are present but may not be well-integrated or effectively used. The presentation allows for understanding but requires effort from the reader.

**Reproducibility:** 2: Low - The paper includes some information about the methods, data, and procedures, but key details are missing. There may be supplementary materials, but they are incomplete or unclear. Reproducing the results would require significant effort and additional information.

**Reviewer Confidence:** 2: Low - The reviewer has some knowledge of the subject area and is somewhat familiar with the research methods and context of the paper. They understand the main points but may lack depth in certain areas. The reviewer is reasonably confident in their assessment but acknowledges some limitations in their expertise.

**Ethics Review Flag:** No

**Ethics Review Description:** Based on the materials reviewed, I found no specific issue requiring a separate ethics review.

---

## Rebuttal Guidelines

Each response is capped at 2,500 characters.

KDD does not allow changes to the paper PDF during the review process. Updated results reflecting reviewer feedback can be included in the rebuttal response (subject to character limits), but reviewers will primarily evaluate the submitted paper. New, unvetted results may be considered in the resubmission decision-making process at the discretion of reviewers.

Experience suggests that effective responses focus on factual errors in the reviews, clarify misunderstandings, and address specific questions posed by the Reviewers. Your response is optional and should be reserved for cases where a response is required.

All the texts you post (rebuttal, and discussion) should not contain any links to external pages. Furthermore, they should not contain any identifying information that may violate the double-blind reviewing policy.
