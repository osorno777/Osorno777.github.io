/*
 * Copyright 1998-2000 Caucho Technology -- all rights reserved
 */

package xsl;

import java.io.*;

import javax.servlet.*;
import javax.servlet.http.*;

/**
 * A simple example of using the same XTP page with multiple stylesheets.
 *
 * Dispatch handles the *.xml extension.  If the filename ends with
 * /plain, use the plain.xsl stylesheet.  Otherwise use the default
 * stylesheet.
 */
public class Dispatch extends GenericServlet {
  public void service(ServletRequest request,
                      ServletResponse response)
    throws IOException, ServletException
  {
    HttpServletRequest req = (HttpServletRequest) request;
    
    // Based on getPathInfo, use either plain.xsl or default.xsl
    
    if ("plain".equals(req.getQueryString())) {
      req.setAttribute("caucho.xsl.stylesheet", "plain.xsl");
    }
    else {
      req.setAttribute("caucho.xsl.stylesheet", "default.xsl");
    }

    // Now forward to the XTP servlet.
    ServletContext app = getServletContext();
    
    RequestDispatcher disp = app.getNamedDispatcher("xtp");

    disp.forward(req, response);  
  }
}
