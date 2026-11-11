# Evaluation on the committed sample notes

Rule: a note is classified genuine when at least 9 of 10 features pass (report's rule).

| Note | Denomination | Label | Features passed | Failed features | Verdict | Correct | Seconds |
|---|---|---|---|---|---|---|---|
| datasets/500_dataset/500_s1.jpg | 500 | real | 10 / 10 | - | likely genuine | yes | 0.30 |
| datasets/500_dataset/500_s2.jpg | 500 | real | 10 / 10 | - | likely genuine | yes | 0.26 |
| datasets/500_dataset/500_s3.jpg | 500 | real | 10 / 10 | - | likely genuine | yes | 0.27 |
| datasets/500_dataset/500_s4.jpg | 500 | real | 8 / 10 | 2, 6 | likely counterfeit | no | 0.23 |
| datasets/500_dataset/500_s5.jpg | 500 | real | 10 / 10 | - | likely genuine | yes | 0.25 |
| datasets/500_dataset/500_s6.jpg | 500 | real | 10 / 10 | - | likely genuine | yes | 0.24 |
| datasets/500_dataset/500_s7.jpg | 500 | real | 9 / 10 | 10 | likely genuine | yes | 0.23 |
| datasets/500_dataset/500_s8.jpg | 500 | real | 9 / 10 | 2 | likely genuine | yes | 0.26 |
| datasets/500_dataset/500_s9.jpg | 500 | real | 10 / 10 | - | likely genuine | yes | 0.25 |
| datasets/500_dataset/500_s10.jpg | 500 | real | 10 / 10 | - | likely genuine | yes | 0.26 |
| datasets/Fake Notes/500/500_f1.jpg | 500 | fake | 7 / 10 | 1, 8, 9 | likely counterfeit | yes | 0.33 |
| datasets/Fake Notes/500/500_f2.jpg | 500 | fake | 6 / 10 | 2, 6, 8, 9 | likely counterfeit | yes | 0.24 |
| datasets/Fake Notes/500/500_f3.jpg | 500 | fake | 7 / 10 | 1, 5, 8 | likely counterfeit | yes | 0.23 |
| datasets/Fake Notes/500/500_f4.jpg | 500 | fake | 6 / 10 | 1, 2, 8, 9 | likely counterfeit | yes | 0.32 |
| datasets/Fake Notes/500/500_f5.jpg | 500 | fake | 6 / 10 | 1, 2, 5, 8 | likely counterfeit | yes | 0.23 |
| datasets/Fake Notes/500/500_f6.jpg | 500 | fake | 8 / 10 | 1, 6 | likely counterfeit | yes | 0.30 |
| datasets/2000_dataset/2000_s1.jpg | 2000 | real | 10 / 10 | - | likely genuine | yes | 0.26 |
| datasets/2000_dataset/2000_s2.jpg | 2000 | real | 10 / 10 | - | likely genuine | yes | 0.28 |
| datasets/2000_dataset/2000_s3.jpg | 2000 | real | 10 / 10 | - | likely genuine | yes | 0.26 |
| datasets/2000_dataset/2000_s4.jpg | 2000 | real | 10 / 10 | - | likely genuine | yes | 0.24 |
| datasets/2000_dataset/2000_s5.jpg | 2000 | real | 10 / 10 | - | likely genuine | yes | 0.25 |
| datasets/2000_dataset/2000_s6.jpg | 2000 | real | 10 / 10 | - | likely genuine | yes | 0.24 |
| datasets/2000_dataset/2000_s7.jpg | 2000 | real | 8 / 10 | 2, 5 | likely counterfeit | no | 0.27 |
| datasets/2000_dataset/2000_s8.jpg | 2000 | real | 9 / 10 | 6 | likely genuine | yes | 0.28 |
| datasets/2000_dataset/2000_s9.jpg | 2000 | real | 8 / 10 | 2, 10 | likely counterfeit | no | 0.28 |
| datasets/Fake Notes/2000/2000_f1.jpg | 2000 | fake | 7 / 10 | 2, 4, 8 | likely counterfeit | yes | 0.29 |
| datasets/Fake Notes/2000/2000_f2.jpg | 2000 | fake | 7 / 10 | 2, 6, 9 | likely counterfeit | yes | 0.22 |
| datasets/Fake Notes/2000/2000_f3.jpg | 2000 | fake | 7 / 10 | 1, 5, 9 | likely counterfeit | yes | 0.22 |
| datasets/Fake Notes/2000/2000_f4.jpg | 2000 | fake | 6 / 10 | 2, 4, 6, 8 | likely counterfeit | yes | 0.27 |
| datasets/Fake Notes/2000/2000_f5.jpg | 2000 | fake | 5 / 10 | 2, 4, 6, 7, 9 | likely counterfeit | yes | 0.38 |
| datasets/Fake Notes/2000/2000_f6.jpg | 2000 | fake | 10 / 10 | - | likely genuine | no | 0.25 |

## Summary

| Scope | Real classified genuine | Fake classified counterfeit | All correct |
|---|---|---|---|
| 500 | 9 / 10 (90.0%) | 6 / 6 (100.0%) | 15 / 16 (93.8%) |
| 2000 | 7 / 9 (77.8%) | 5 / 6 (83.3%) | 12 / 15 (80.0%) |
| overall | 16 / 19 (84.2%) | 11 / 12 (91.7%) | 27 / 31 (87.1%) |

Mean seconds per note: 0.26

Original report: 15 / 19 real notes and 10 / 12 fake notes classified correctly.
