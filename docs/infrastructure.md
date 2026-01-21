# implementing a naming convention 
problem: If you decide to change the naming convention (e.g., adding the environment suffix -dev), you have to go into every module's code and change how they handle that string.
fix: You should construct the Final Name in the root locals and pass the completed string to the modules. The modules shouldn't have to "think" about the naming convention; they should just receive a name and use it.

## locals vs variables 
- synthesis: 
  - Variables are used for things that *must change* depending on the user (mutability)
    - e.g., "Which region are we in?". 
  - Locals are used for things that are *calculated or constant* (immutability)
- there difference reside on their **Scope**
  - A Local is only accessible within the local module vs a Terraform variable, which can be scoped globally.
- mutability and immutability:
  - A *local* doesn’t change its value once assigned. A variable value can be manipulated via expressions 
    - This makes it easier to assign expression outputs to locals and use that throughout the code instead of using the expression itself at multiple places.

# for_each vs Singleton for s3 buckets creation (infra/modules/storage)
Used `for_each` with a Map to ensure scalability and enforce uniform security policies across all Lakehouse layers.



