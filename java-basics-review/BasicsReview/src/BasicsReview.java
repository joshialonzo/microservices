import java.awt.*;
import java.util.ArrayList;
import java.util.List;

public class BasicsReview {

    public static void main(String[] args) {
        // Print a string
        String myVariable = "Example Value";
        System.out.println(
                "The value of my variable is: " + myVariable
        );

        // Print an integer
        Integer myInt = 3;
        System.out.println(
                "The value of my integer is: " + myInt
        );

        // Print the result of a function
        BasicsReview basics = new BasicsReview();
        System.out.println(basics.addNumbers(2, 4));

        // Print an array
        basics.printArray();

        // Print a list
        basics.printList();

        // Print conditional statements
        basics.printConditionalStatement();
    }

    int addNumbers(int num1, int num2) {
        return num1 + num2;
    }

    void printArray() {
        String[] myArray = new String[3];
        myArray[0] = "Hi";
        myArray[1] = "I'm";
        myArray[2] = "Joshi";
        for (String value : myArray) {
            System.out.print(value + " ");
        }
        System.out.println();
    }

    void printList() {
        List<String> myList = new ArrayList<>();
        myList.add("Hi");
        myList.add("I'm");
        myList.add("Josue");
        for (String value : myList) {
            System.out.print(value + " ");
        }
        System.out.println();
    }

    void printConditionalStatement() {
        Integer myInteger = null;
        if (myInteger != null) {
            System.out.println(myInteger.toString());
        } else {
            System.out.println("My Integer is null.");
        }
    }
}
