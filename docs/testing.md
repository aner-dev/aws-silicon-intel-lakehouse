# 3 types of testing
The difference lies in **Dependencies.**
# unit tests 
- test the internal logic, a single 'unit' of code in total isolation (a function or a class)
  - example file: `tests/test_spark.py`
- YES mock
-   - "Faking" the outside world to focus only on the logic inside the function.
- replace real entities and tools with placeholders & simulation 
- # integration tests
- **test connectivity**
- testing how 2 or more entities or components works together
  - example file: `tests/test_observability_suite.py`
- NOT mock 
- # smoke tests
- the most 'small', they check if engines can actually start 
-   - like a 'Power On' button
- NOT mock
