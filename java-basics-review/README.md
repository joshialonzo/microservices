# Java Basics Review

A hands-on review of core Java fundamentals, organized as an IntelliJ IDEA project.

## Topics Covered

| Topic | Description |
|---|---|
| Variables | Declaring and printing `String` and `Integer` variables |
| Methods | Defining and calling instance methods (e.g. `addNumbers`) |
| Arrays | Creating and iterating over fixed-size `String[]` arrays |
| Lists | Using `ArrayList<>` with a for-each loop |
| Conditionals | Null-check with `if/else` |
| Classes & Packages | Defining a `Person` class with private fields and getters/setters |
| User Input | Reading console input with `Scanner` |
| File I/O | Reading a text file with `Scanner` and handling `FileNotFoundException` |
| List Sum | Summing integers in an `ArrayList` with a for-each loop |

## Project Structure

```
BasicsReview/
├── assets/
│   └── example.txt          # Sample text file used in the file-reading exercise
└── src/
    └── com/joshialonzo/exampleapp/
        ├── BasicsReview.java # Main class — entry point and all exercises
        └── Person.java       # Simple POJO with name field
```

## Running the Project

Open `BasicsReview/` in IntelliJ IDEA and run `BasicsReview.java` as the main class.

> The program prompts for console input (name entry), so run it in a terminal or the IntelliJ run console.

## Requirements

- Java 8+
- IntelliJ IDEA (or any Java IDE / `javac` on the command line)
