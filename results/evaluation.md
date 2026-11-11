# Evaluation on the committed sample notes

Rule: a note is classified genuine when at least 9 of 10 features pass (report's rule).

| Note | Denomination | Label | Features passed | Failed features | Verdict | Correct | Seconds |
|---|---|---|---|---|---|---|---|
| datasets/500_dataset/500_s1.jpg | 500 | real | 10 / 10 | - | likely genuine | yes | 0.41 |
| datasets/500_dataset/500_s2.jpg | 500 | real | 10 / 10 | - | likely genuine | yes | 0.44 |
| datasets/500_dataset/500_s3.jpg | 500 | real | 10 / 10 | - | likely genuine | yes | 0.46 |
| datasets/500_dataset/500_s4.jpg | 500 | real | 8 / 10 | 2, 6 | likely counterfeit | no | 0.40 |
| datasets/500_dataset/500_s5.jpg | 500 | real | 9 / 10 | 2 | likely genuine | yes | 0.41 |
| datasets/500_dataset/500_s6.jpg | 500 | real | 10 / 10 | - | likely genuine | yes | 0.41 |
| datasets/500_dataset/500_s7.jpg | 500 | real | 9 / 10 | 10 | likely genuine | yes | 0.42 |
| datasets/500_dataset/500_s8.jpg | 500 | real | 8 / 10 | 2, 6 | likely counterfeit | no | 0.44 |
| datasets/500_dataset/500_s9.jpg | 500 | real | 10 / 10 | - | likely genuine | yes | 0.43 |
| datasets/500_dataset/500_s10.jpg | 500 | real | 9 / 10 | 6 | likely genuine | yes | 0.46 |
| datasets/Fake Notes/500/500_f1.jpg | 500 | fake | 7 / 10 | 1, 8, 9 | likely counterfeit | yes | 0.61 |
| datasets/Fake Notes/500/500_f2.jpg | 500 | fake | 6 / 10 | 2, 6, 8, 9 | likely counterfeit | yes | 0.41 |
| datasets/Fake Notes/500/500_f3.jpg | 500 | fake | 7 / 10 | 1, 5, 8 | likely counterfeit | yes | 0.40 |
| datasets/Fake Notes/500/500_f4.jpg | 500 | fake | 6 / 10 | 1, 2, 8, 9 | likely counterfeit | yes | 0.59 |
| datasets/Fake Notes/500/500_f5.jpg | 500 | fake | 6 / 10 | 1, 2, 5, 8 | likely counterfeit | yes | 0.39 |
| datasets/Fake Notes/500/500_f6.jpg | 500 | fake | 9 / 10 | 6 | likely genuine | no | 0.55 |
| datasets/2000_dataset/2000_s1.jpg | 2000 | real | 10 / 10 | - | likely genuine | yes | 0.46 |
| datasets/2000_dataset/2000_s2.jpg | 2000 | real | 10 / 10 | - | likely genuine | yes | 0.45 |
| datasets/2000_dataset/2000_s3.jpg | 2000 | real | 10 / 10 | - | likely genuine | yes | 0.45 |
| datasets/2000_dataset/2000_s4.jpg | 2000 | real | 10 / 10 | - | likely genuine | yes | 0.42 |
| datasets/2000_dataset/2000_s5.jpg | 2000 | real | 10 / 10 | - | likely genuine | yes | 0.46 |
| datasets/2000_dataset/2000_s6.jpg | 2000 | real | 10 / 10 | - | likely genuine | yes | 0.45 |
| datasets/2000_dataset/2000_s7.jpg | 2000 | real | 8 / 10 | 2, 6 | likely counterfeit | no | 0.48 |
| datasets/2000_dataset/2000_s8.jpg | 2000 | real | 9 / 10 | 6 | likely genuine | yes | 0.52 |
| datasets/2000_dataset/2000_s9.jpg | 2000 | real | 8 / 10 | 2, 10 | likely counterfeit | no | 0.49 |
| datasets/Fake Notes/2000/2000_f1.jpg | 2000 | fake | 7 / 10 | 2, 4, 8 | likely counterfeit | yes | 0.52 |
| datasets/Fake Notes/2000/2000_f2.jpg | 2000 | fake | 7 / 10 | 2, 6, 9 | likely counterfeit | yes | 0.42 |
| datasets/Fake Notes/2000/2000_f3.jpg | 2000 | fake | 7 / 10 | 1, 5, 9 | likely counterfeit | yes | 0.42 |
| datasets/Fake Notes/2000/2000_f4.jpg | 2000 | fake | 6 / 10 | 2, 4, 6, 8 | likely counterfeit | yes | 0.52 |
| datasets/Fake Notes/2000/2000_f5.jpg | 2000 | fake | 5 / 10 | 2, 4, 6, 7, 9 | likely counterfeit | yes | 0.70 |
| datasets/Fake Notes/2000/2000_f6.jpg | 2000 | fake | 10 / 10 | - | likely genuine | no | 0.48 |

## Summary

| Scope | Real classified genuine | Fake classified counterfeit | All correct |
|---|---|---|---|
| 500 | 8 / 10 (80.0%) | 5 / 6 (83.3%) | 13 / 16 (81.2%) |
| 2000 | 7 / 9 (77.8%) | 5 / 6 (83.3%) | 12 / 15 (80.0%) |
| overall | 15 / 19 (78.9%) | 10 / 12 (83.3%) | 25 / 31 (80.6%) |

Mean seconds per note: 0.47

Original report: 15 / 19 real notes and 10 / 12 fake notes classified correctly.
