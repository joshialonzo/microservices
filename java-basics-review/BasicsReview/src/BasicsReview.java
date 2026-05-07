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
    }

    int addNumbers(int num1, int num2) {
        return num1 + num2;
    }
}
