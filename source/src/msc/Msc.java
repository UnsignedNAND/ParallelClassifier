package msc;

import parser.WikiParser;

public class Msc {

    public static void main(String[] args) {
        WikiParser wp;
        wp = new WikiParser();
        wp.Parse();
        wp.PrintList();
    }
}
