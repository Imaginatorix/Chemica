# Chemica - Chemical Engine
**Version 1.0.0**
## A simple chemical reaction calculator website

### Video Demo:
https://youtu.be/XwiljT8qiPI

### Join Info:
https://chemica-chemcal.herokuapp.com/

### Motivation of Project
I've been a watching a lot of NileRed's youtube channel for a time now and, with the combination of my 9th Grade Chemistry Teacher's enthusiasm in teaching, I found myself wanting to try and create several compounds with interesting properties. I've never been in a Chem lab personally, so I can only imagine. This "craving" for combining several compounds gave me the thought of a chemical reaction predictor, the main purpose of which is to test a set of reactants and find the respective product that reflects to the real world. There are several reasons why I want to realize this thought.

Seeing it with the option of all different conceivable processes, I've essentially imagined an electronic-Chemistry lab or a Chemical Engine where you can test and see the processes of how different chemicals are formed (which could otherwise be lethal for the people in the lab) without buying the chemicals and/or 'wasting' the chemicals testing or experimenting several combinations to reach a desired output.

Although version 1.0.0 did not do what I envisioned yet, I think, it is a good first step. I am still yet to learn more Chemistry.

### What does it do?
**Version 1.0.0**

The calculator can:\
(a) predict the theorized products given reactants A and B\
(b) give the Lewiss Structure\
(c) methodically name substances\
(d) balance the reaction (via chempy)

### Dependencies
This project utilizes three main dependencies:\
(a) [chempy](https://pythonhosted.org/chempy/) - which is a package for solving problems in chemistry. I used it:
- (i) for the balancing of the chemical equations
- (ii) for the identification of the compound composition

(b) [mendeleev](https://mendeleev.readthedocs.io/en/stable/quick.html) - which is a package for accessing various properties of elements, ions, and isotopes in the periodic table of elements. I used it:
- (i) for the properties of the elements

(c) [PIL](https://pillow.readthedocs.io/en/stable/) - which is a Python Imaging Library. I used it:
- (i) for drawing the Lewis Structure

### How it works?
(a) Predictor
- (i) Get composition for both reactants
- (ii) Identify most possible type of reaction
- (iii) Run respective reaction (see details in [run.py](chemica/run.py))
- (iv) Balance reaction (via chempy)
- (v) Turn to wanted format (str or dict)

(b) Lewiss Structure Generator
- (i) Identify center (least electronegative, Carbon +1 priority, Hydrogen -1 priority)
- (ii) Connect all connections by a single bond
- (iii) Count extra electrons
- (iv) Distribute electrons to make connections follow the octet rule

(c) Naming substances
- (i) Get element name
- (ii) Identify prefix using the number of same atoms and position on the compound
- (iii) Add -ide suffix

(d) Balance Reaction (via chempy)
- (i) Use chempy's chemistry.balance_stoichiometry method

### Decisions:
(a) API
Initially, I thought of using an online API and just query for the information. By implementing so, I won't personally be needing to update the information. What I had in mind was something like [this](https://github.com/neelpatel05/periodic-table-api-go), fast and reliable. However, I changed my mind when I found some well-established libraries, such as [mendeleev](https://mendeleev.readthedocs.io/en/stable/quick.html), which are generally a lot faster than querying. The problem is, I will be needing to update it from time to time because it is downloaded (although with the help of github, I don't think that's much of a problem).

(b) App vs Website
I chose to create a website instead of an app as I think it would be better if the users won't need to configure their system to run the program (i.e. downloading code from github and python, with dependencies, to be able to run said code).

(c) Predictor Procedure
I wanted to make this process as generalized as possible. However, on my 'research,' I wasn't able to find such way. For now, I went with the identify -> predict apporach, which is pretty limited and sometimes incorrect, but that'll do for now. See Known Issues (a).

### Plans on the future:
(a) Type of procedure the reactants will go through
(b) Properties of the chemicals
(c) Uses of the chemicals
(d) Visualizations of molecules - [might be useful](https://stackoverflow.com/questions/65187916/using-glowscript-to-create-widgets-and-graphics-in-different-divs)
(e) Fix Issues

### Known Issues:
(a) The prediction process is not very generalized, making some combinations unpredictable or wrongly predicted.
(b) Considers each element in the polyatomic atom as different or can't identify polyatomic atoms.
(c) Can't distinguish between ionic and covalent bonding in Lewiss Structure.

---
### License & Copyright
See the [LICENSE](LICENSE.md) file for license rights and limitations (MIT).
