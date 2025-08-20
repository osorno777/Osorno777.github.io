/*
 * Copyright 1998-1998 Caucho Technology -- all rights reserved
 *
 * Caucho Technology forbids redistribution of any part of this software
 * in any form, including derived works and generated binaries.
 *
 * This Software is provided "AS IS," without a warranty of any kind. 
 * ALL EXPRESS OR IMPLIED REPRESENTATIONS AND WARRANTIES, INCLUDING ANY
 * IMPLIED WARRANTY OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE
 * OR NON-INFRINGEMENT, ARE HEREBY EXCLUDED.

 * CAUCHO TECHNOLOGY AND ITS LICENSORS SHALL NOT BE LIABLE FOR ANY DAMAGES
 * SUFFERED BY LICENSEE OR ANY THIRD PARTY AS A RESULT OF USING OR
 * DISTRIBUTING SOFTWARE. IN NO EVENT WILL Caucho OR ITS LICENSORS BE LIABLE
 * FOR ANY LOST REVENUE, PROFIT OR DATA, OR FOR DIRECT, INDIRECT, SPECIAL,
 * CONSEQUENTIAL, INCIDENTAL OR PUNITIVE DAMAGES, HOWEVER CAUSED AND
 * REGARDLESS OF THE THEORY OF LIABILITY, ARISING OUT OF THE USE OF OR
 * INABILITY TO USE SOFTWARE, EVEN IF HE HAS BEEN ADVISED OF THE POSSIBILITY
 * OF SUCH DAMAGES.      
 *
 * @author Scott Ferguson
 *
 * $Id: HelloServlet.java,v 1.1 2000/01/19 23:53:21 ferg Exp $
 */

import java.io.*;
import java.util.*;

import javax.servlet.http.*;
import javax.servlet.*;

public class HelloServlet extends HttpServlet {
  public void doGet (
	HttpServletRequest	req,
	HttpServletResponse	res
    ) throws ServletException, IOException
  {
    res.setContentType("text/html");
    PrintWriter pw = res.getWriter();

    pw.println("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0 Transitional//EN\">");
    pw.println();
    pw.println("<head>");
    pw.println("<meta http-equiv=\"Content-Type\" content=\"text/html; charset=ISO-8859-1\">");
    pw.println();
    pw.println("<!-- The Servlet expression tags interpolate script variables into the HTML -->");
    pw.println();
    pw.println("<title>Hello, world!</title>");
    pw.println("</head>");
    pw.println();
    pw.println("<body bgcolor=#cc99dd>");
    pw.println();
    pw.println("<h1>Hello, world!</h1>");
    pw.println();
    pw.println("</body>");
    pw.close();
  }

  public HelloServlet() {}
}
