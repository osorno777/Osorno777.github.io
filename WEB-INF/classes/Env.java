/*
 * Copyright 1998-1999 Caucho Technology.  All rights reserved.
 */

import java.io.*;
import java.util.*;

import javax.servlet.http.*;
import javax.servlet.*;

/**
 * The Env servlet prints the values of most of the Servlet API.
 */
public class Env extends GenericServlet {
  public void service(
	ServletRequest	req,
	ServletResponse	res
    ) throws ServletException, IOException
  {
    HttpServletRequest request = (HttpServletRequest) req;
    HttpServletResponse response = (HttpServletResponse) res;

    /*
     * Get a PrintWriter to write the text.
     */
    response.setContentType("text/html");
    PrintWriter pw = response.getWriter();

    /*
     * Print the header.
     */
    pw.println("<html>");
    pw.println("<head><title>Environment Script</title></head>");
    pw.println("<body bgcolor=#ffffff>");
    pw.println();

    /*
     * And the request URL
     */
    pw.println("<h1>Requested URL:</h1>");
    pw.println("<pre>");
    pw.println(HttpUtils.getRequestURL(request));
    pw.println("</pre>");

    /*
     * Print request variables
     */
    printRequest(pw, request);

    /*
     * Print form values
     */
    printForm(pw, request);

    /*
     * Print session values
     */
    printSession(pw, request);

    /*
     * Print application values
     */
    printApplication(pw, request);

    /*
     * Print servlet init parameters
     */
    printServletInit(pw);

    /*
     * Print application init parameters
     */
    printApplicationInit(pw);

    /*
     * Write the footer
     */

    pw.println("</body>");
    pw.println("</html>");
  }

  /**
   * Write the properties of the request object
   */
  private void printRequest(PrintWriter pw, HttpServletRequest request)
    throws IOException
  {
    pw.println("<h1>Request Information:</h1>");
    pw.println("<table>");
    pw.print("<tr><td>Request method      <td>");
    pw.println(request.getMethod());
    pw.print("<tr><td>Request URI         <td>");
    pw.println(request.getRequestURI());
    pw.print("<tr><td>Request protocol    <td>");
    pw.println(request.getProtocol());
    pw.print("<tr><td>Servlet path        <td>");
    pw.println(request.getServletPath());
    pw.print("<tr><td>Path info           <td>");
    pw.println(request.getPathInfo());
    pw.print("<tr><td>Path translated     <td>");
    pw.println(request.getPathTranslated());
    pw.print("<tr><td>Query string        <td>");
    pw.println(request.getQueryString());
    pw.print("<tr><td>Content length      <td>");
    pw.println(request.getContentLength());
    pw.print("<tr><td>Content type        <td>");
    pw.println(request.getContentType());
    pw.print("<tr><td>Server name         <td>");
    pw.println(request.getServerName());
    pw.print("<tr><td>Server port         <td>");
    pw.println(request.getServerPort());
    pw.print("<tr><td>Remote user         <td>");
    pw.println(request.getRemoteUser());
    pw.print("<tr><td>Remote address      <td>");
    pw.println(request.getRemoteAddr());
    pw.print("<tr><td>Remote host         <td>");
    pw.println(request.getRemoteHost());
    pw.print("<tr><td>Authorization scheme<td>");
    pw.println(request.getAuthType());
    pw.println("</table>");

    /*
     * Write the HTTP request headers.
     */
    pw.println("<h1>Request Headers:</h1>");
    pw.println("<table>");

    Enumeration e = request.getHeaderNames();
    while (e.hasMoreElements()) {
      String name = (String) e.nextElement();

      pw.print("<tr><td>");
      pw.print(name);
      pw.print("<td>");
      pw.println(request.getHeader(name));
    }

    pw.println("</table>");

    /*
     * Write any request attributes
     */
    pw.println("<h1>Request Attributes:</h1>");
    pw.println("<table>");

    e = request.getAttributeNames();
    while (e.hasMoreElements()) {
      String name = (String) e.nextElement();

      pw.print("<tr><td>");
      pw.print(name);
      pw.print("<td>");
      pw.println(request.getAttribute(name));
    }

    pw.println("</table>");
  }

  /**
   * Write any form values
   */
  private void printForm(PrintWriter pw, HttpServletRequest request)
    throws IOException
  {
    pw.println("<h1>Form Values:</h1>");
    pw.println("<table>");

    Enumeration e = request.getParameterNames();
    while (e.hasMoreElements()) {
      String name = (String) e.nextElement();

      pw.print("<tr><td>");
      pw.print(name);
      pw.print("<td>");
      pw.println(request.getParameter(name));
    }

    pw.println("</table>");
  }

  /**
   * Write session properties
   */
  private void printSession(PrintWriter pw, HttpServletRequest request)
    throws IOException
  {
    HttpSession session = request.getSession(false);
    if (session == null) {
      pw.println("<h1>No Session</h1>");
      return;
    }

    pw.println("<h1>Session Information:</h1>");
    pw.println("<table>");
    pw.print("<tr><td>Id<td>");
    pw.println(session.getId());
    pw.print("<tr><td>isNew<td>");
    pw.println(session.isNew());
    pw.println("</table>");

    pw.println("<h1>Session Variables:</h1>");
    pw.println("<table>");

    String []names = session.getValueNames();
    for (int i = 0; i < names.length; i++) {
      String name = names[i];

      pw.print("<tr><td>");
      pw.print(name);
      pw.print("<td>");
      pw.println(session.getValue(name));
    }

    pw.println("</table>");
  }

  /**
   * Write application properties
   */
  private void printApplication(PrintWriter pw, HttpServletRequest req)
    throws IOException
  {
    ServletContext application = getServletContext();

    pw.println("<h1>Application Information:</h1>");
    pw.println("<table>");
    pw.print("<tr><td>Major Version<td>");
    pw.println(application.getMajorVersion());
    pw.print("<tr><td>Minor Version<td>");
    pw.println(application.getMinorVersion());
    pw.print("<tr><td>Server Info<td>");
    pw.println(application.getServerInfo());
    pw.print("<tr><td>Real Path (of pathinfo)<td>");
    pw.println(application.getRealPath(req.getPathInfo()));
    pw.print("<tr><td>Mime-type (of pathinfo)<td>");
    pw.println(application.getMimeType(req.getPathInfo()));
    pw.println("</table>");

    pw.println("<h1>Application Variables:</h1>");
    pw.println("<table>");

    Enumeration e = application.getAttributeNames();
    while (e.hasMoreElements()) {
      String name = (String) e.nextElement();

      pw.print("<tr><td>");
      pw.print(name);
      pw.print("<td>");
      pw.println(application.getAttribute(name));
    }

    pw.println("</table>");
  }

  /**
   * Write servlet init parameters
   */
  private void printServletInit(PrintWriter pw)
    throws IOException
  {
    Enumeration e = getInitParameterNames();
    
    if (! e.hasMoreElements())
      return;

    pw.println("<h1>Servlet Init Parameters:</h1>");
    pw.println("<table>");

    while (e.hasMoreElements()) {
      String name = (String) e.nextElement();

      pw.print("<tr><td>");
      pw.print(name);
      pw.print("<td>");
      pw.println(getInitParameter(name));
    }

    pw.println("</table>");
  }

  /**
   * Write application init parameters
   */
  private void printApplicationInit(PrintWriter pw)
    throws IOException
  {
    ServletContext app = getServletContext();
    
    Enumeration e = app.getInitParameterNames();
    
    if (! e.hasMoreElements())
      return;

    pw.println("<h1>Application Init Parameters:</h1>");
    pw.println("<table>");

    while (e.hasMoreElements()) {
      String name = (String) e.nextElement();

      pw.print("<tr><td>");
      pw.print(name);
      pw.print("<td>");
      pw.println(app.getInitParameter(name));
    }

    pw.println("</table>");
  }
}
