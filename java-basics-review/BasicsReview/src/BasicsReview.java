public class BasicsReview {

    public static void main(String[] args) {
        String myVariable = "Example Value";
        System.out.println(
                "The value of my variable is: " + myVariable
        );

        Integer myInt = 3;
        System.out.println(
                "The value of my integer is: " + myInt
        );

        BasicsReview basics = new BasicsReview();
        System.out.println(basics.addNumbers(2, 4));

        basics.printArray();
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
    }
}
