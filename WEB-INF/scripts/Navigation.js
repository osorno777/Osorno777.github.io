/** -*- Java -*-
 * The Navigation class provides a set of routines for creating navigation.
 *
 * It implements three useful navigation techniques: 
 *   family navigation,
 *   threaded (prev/next) pages, 
 *   table of contents.
 *
 * Each Navigation contains the table of contents read in from the toc.xml
 * file in the current directory.
 *
 * Calling scripts can test if the toc.xml is obsolete by testing isObsolete(),
 * so clever pages can just store the toc in the application object, speeding
 * things up.
 */
class Navigation {
  /**
   * The class constructor reads in the xml file.
   */
  function Navigation()
  {
    this.file = File("toc.xml");
    this.lastModified = this.file.lastModified;

    this.toc = caucho.xml.LooseXml.parseFile(this.file);
  }

  /**
   * Returns true if the file has changed from the version stored in
   * this class.
   */
  function isObsolete()
  {
    return this.lastModified < this.file.lastModified;
  }

  /**
   * Writes the family navigation.  This is in three parts:
   *
   *  ancestors
   *  ---------
   *  siblings
   *  ---------
   *  children.
   *
   * The navigation generates rows of a one column table.  The caller
   * is responsible for creating the table itself.
   */
  function writeFamilyNavigation(out, uri)
  {
    var name = uri.match(/[^\/]*$/)[0];

    var here = this.getHere(name);
    if (! here)
      return;
    var parents = this.getParents(here);
    if (parents)
      var navList = parents.concat([null]);
    else
      var navList = [];

    navList = navList.concat(this.getSiblings(here));
    var children = this.getChildren(here);
    if (children.length)
      navList = navList.concat([null], children)

    for (var i = 0; i < navList.length; i++) {
      var item = navList[i];

      if (! item) {
        out.writeln("<hr>");
        continue;
      }

      var href = item.attribute.href;
      var name = item.attribute.name;
      if (! href || item == here)
       out.writeln(@'<em>$(name)</em><br>');
      else
        out.writeln(@'<a href="$(href)">$(name)</a><br>');
    }
  }

  /**
   * Returns an array of the parent pages.
   */
  function getParents(here)
  {
    var parents = [];
    for (var node = here.parentNode; node; node = node.parentNode) {
      if (node.nodeName == 'page')
        parents.unshift(node);
    }

    return parents;
  }

  /**
   * Returns an array of sibling pages.
   */
  function getSiblings(here)
  {
    var siblings = [];
    for (var node in here.select("../page"))
      siblings.push(node);

    return siblings;
  }

  /*
   * Returns an array of child nodes.
   */
  function getChildren(here)
  {
    var children = [];
    for (var node in here.select("page"))
      children.push(node);

    return children;
  }


  /**
   * Writes the table of contents.
   */
  function writeContents(out, uri)
  {
    var here = this.getHere(uri);

    if (here == null)
      return;

    this.writeContentsRec(out, here.parentNode);
  }

  /**
   * Recursively creates a table of contents.  Essentially a list of lists.
   */
  function writeContentsRec(out, here)
  {
    var hasContents = false;
    var iter = here.select("page");

    if (iter.hasNext()) {
      out.writeln("<ol>");

      for (var node in iter) {
        out.writeln("<li><a href='", node.attribute.href, "'>",
  	            node.attribute.name, "</a>");
        this.writeContentsRec(out, node);
      }

      out.writeln("</ol>");
    }
  }

  /**
   * Writes previous and next nodes for a threaded list of pages.  Useful
   * for something like a manual.
   */
  function writePrevNext(out, uri)
  {
    var here = this.getHere(uri);

    out.writeln("<table border=0 width='100%'><tr>");
    out.writeln("<td>");

    var prev = this.getPreviousPage(here);
    if (prev && prev.attribute.href)
      out.writeln("<a href='", prev.attribute.href, "'>",
	          prev.attribute.name, "</a>");
    else if (prev)
      out.writeln(prev.attribute.name);

    out.writeln("<td align=center width='*'>&nbsp;");
    out.writeln("</td><td align=right>");

    var next = this.getNextPage(here);
    if (next && next.attribute.href)
      out.writeln("<a href='", next.attribute.href, "'>",
	          next.attribute.name, "</a>");
    else if (next)
      out.writeln(next.attribute.name);

    out.writeln("</table>");
  }

  /**
   * Returns the previous page.  It keeps going through the previous nodes
   * until it find a page element.
   */
  function getPreviousPage(here)
  {
    for (var page = this.getPrevious(here); 
         page; 
         page = this.getPrevious(page)) {
      if (page.nodeType == page.ELEMENT_NODE && page.nodeName == "page")
        return page;
    }

    return null;
  }
  /**
   * Returns the previous node in a fictitious depth first search of the
   * XML tree.  Tragically, the W3C hasn't defined a standard function for
   * this.
   */
  function getPrevious(here)
  {
    if (! here)
      return null;

    if (here.previousSibling) {
      here = here.previousSibling;
      for (; here.lastChild; here = here.lastChild) {
      }
      return here;
    }

    return here.parentNode;
  }

  /**
   * Returns the next page in the table of contents.
   */
  function getNextPage(here)
  {
    for (var page = this.getNext(here); 
         page; 
         page = this.getNext(page)) {
      if (page.nodeType == page.ELEMENT_NODE && page.nodeName == "page")
        return page;
    }

    return null;
  }

  /**
   * Returns the next node in a fictitious depth first search of the XML
   * tree
   */
  function getNext(here)
  {
    if (! here)
      return null;

    if (here.firstChild)
      return here.firstChild;

    for (; here; here = here.parentNode) {
      if (here.nextSibling)
        return here.nextSibling;
    }

    return null;
  }

  /**
   * Returns the node pointing to href.  href is the tail of the current
   * URI.
   */
  function getHere(uri)
  {
    var href = uri.match(/[^\/]*$/)[0];

    return this.toc.find(@"//page[@href='$href']");
  }
}

/**
 * Gets the navigation.  If a valid version is stored in the application
 * object, use it.  Otherwise, create a new Navigation object.
 */
function getNavigation(application)
{
  var navigation = application.attribute["navigation"];

  if (navigation == null || navigation.isObsolete()) {
    navigation = new Navigation();
    application.attribute["navigation"] = navigation;
  }

  return navigation;
}

Navigation.getNavigation = getNavigation

