/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package parser;

import org.junit.After;
import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import static org.junit.Assert.*;

/**
 *
 * @author mszankin
 */
public class PrepareTextTest {
    
    public PrepareTextTest() {
    }
    
    @BeforeClass
    public static void setUpClass() {
    }
    
    @AfterClass
    public static void tearDownClass() {
    }
    
    @Before
    public void setUp() {
    }
    
    @After
    public void tearDown() {
    }

    /**
     * Test of Stemm method, of class PrepareText.
     */
    @Test
    public void testStemm() {
        System.out.println("Stemm");
        String str = "";
        String expResult = "";
        String result = PrepareText.Stemm(str);
        assertEquals(expResult, result);
        // TODO review the generated test code and remove the default call to fail.
        fail("The test case is a prototype.");
    }

    /**
     * Test of TrimWhiteSpaces method, of class PrepareText.
     */
    @Test
    public void testTrimWhiteSpaces() {
        System.out.println("TrimWhiteSpaces");
        String str = "";
        String expResult = "";
        String result = PrepareText.TrimWhiteSpaces(str);
        assertEquals(expResult, result);
        // TODO review the generated test code and remove the default call to fail.
        fail("The test case is a prototype.");
    }

    /**
     * Test of LowerString method, of class PrepareText.
     */
    @Test
    public void testLowerString() {
        System.out.println("LowerString");
        String str = "AbC DeF";
        String expResult = "abc def";
        String result = PrepareText.LowerString(str);
        assertEquals(expResult, result);
    }
    
}
