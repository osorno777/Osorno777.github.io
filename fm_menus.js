// Menu Script
// Based on a script by Peter Belesis. v3.10.1 000630 (http://www.dhtmlab.com/)

// Main Script Start

window.onload = startIt;
if(NS4){
	origWidth       = window.innerWidth;
	origHeight      = window.innerHeight;
	window.onresize = reDo;
}

// Defaults
menuWidth    = 120;
fntCol       = "blue";
fntBold      = false;
fntItal      = false;
fntFam       = "arial,helvetica,sans-serif";
backCol      = "#cccccc";
overCol      = "#9999ff";
overFnt      = "red";
borWid       = 2;
borCol       = "black";
borSty       = "solid";
itemPad      = 1;
separator    = 0;
separatorCol = "black";
deltaX       = 5;
deltaY       = 9;
// End defaults

isLoaded     = false;
NSresized    = false;
areCreated   = false;
menuLoc      = null;
if (fntSiz < 8) fntSiz = 8;

function initVars() {
	topCount     = 1;
	areCreated   = false;
	beingCreated = false;
	isOverMenu   = false;
	currentMenu  = null;
}

initVars();

function startIt() {
	isLoaded = true;
	menuLoc = window;
	menuLoc.nav  = window;
    if (NS4) menuLoc.document.captureEvents(Event.MOUSEDOWN);
    menuLoc.document.onmousedown = clicked;
	makeTop();   
}

function makeTop(){
	beingCreated = true;
	if(IE4) {
		topZ = 0;
		for (z=0;z<menuLoc.document.all.length;z++){
			oldEl = menuLoc.document.all(z);
			topZ = Math.max(oldEl.style.zIndex,topZ);
		}
	}
	while(eval("window.arMenu" + topCount)) {
		(NS4) ? makeMenuNS(topCount) : makeMenuIE(topCount);
		topCount++
	}

	areCreated   = true;
	beingCreated = false;
}

function makeMenuNS(menuCount) {
	tempArray = eval("arMenu" + menuCount);
	
	tempWidth        = tempArray[0] ? tempArray[0] : menuWidth;
	menu             = makeElement("elMenu" + menuCount,tempWidth,null);
	menu.array       = tempArray;
	menu.setMenuTree = setMenuTree;
	menu.setMenuTree();

	while (menu.itemCount < menu.maxItems) {
		menu.itemCount++;
		prevItem = (menu.itemCount > 1) ? menu.item : null;
		itemName = "item" + menuCount + "_" + menu.itemCount;

		menu.item = makeElement(itemName,null,menu);

		menu.item.prevItem = prevItem;
		menu.item.setup = itemSetup;
		menu.item.setup(menu.itemCount,menu.array);
	}
	menu.lastItem = menu.item;
	menu.setup();
}

function setMenuTree() {
    this.menuWidth        = this.array[0] ? this.array[0] : menuWidth;
    this.menuLeft         = "";
    this.menuTop          = "";
    this.menuFontColor    = fntCol;
    this.menuFontOver     = overFnt;
    this.menuBGColor      = backCol;
    this.menuBGOver       = overCol;
    this.menuBorCol       = borCol;
    this.menuSeparatorCol = separatorCol;
	this.maxItems         = (this.array.length-1)/2;
	this.setup            = menuSetup;
	this.itemCount        = 0;
}

function makeMenuIE(menuCount) {
	menu             = makeElement("elMenu" + menuCount);
	menu.array       = eval("arMenu" + menuCount);
	menu.setMenuTree = setMenuTree;
	menu.setMenuTree();
	menu.itemStr     = "";
	
	while (menu.itemCount < menu.maxItems) {
		menu.itemCount++;
		itemName = "item" + menuCount + "_" + menu.itemCount;

		arrayPointer = ((menu.itemCount-1)*2)+1;
		dispText     = menu.array[arrayPointer];

		if(IE5) {
			newSpan = menuLoc.document.createElement("SPAN");
			with(newSpan) {
				id = itemName;
				with(style) {
					width      = (menu.menuWidth-(borWid*2));
					fontSize   = fntSiz + "pt";
					fontWeight = (fntBold) ? "bold"   : "normal";
					fontStyle  = (fntItal) ? "italic" : "normal";
					fontFamily = fntFam;
					padding    = itemPad;

					borderBottomWidth = separator + "px";
					borderBottomStyle = "solid";
				}
				innerHTML = dispText;
			}
	
			newBreak = menuLoc.document.createElement("BR");
			menu.appendChild(newSpan);
			menu.appendChild(newBreak);
		}
		else {
			htmStr = dispText;

            menu.itemStr += "<SPAN ID=" + itemName + ' STYLE="width:' + (menu.menuWidth-(borWid*2)) + '">' + htmStr + "</SPAN><BR>";
		}
	}

	if(!IE5) menu.innerHTML = menu.itemStr;

	itemColl = menu.children.tags("SPAN");
	for (i=0; i<itemColl.length; i++) {
		it = itemColl(i);
		it.setup = itemSetup;
		it.setup(i+1,menu.array);
	}
	menu.lastItem = itemColl(itemColl.length-1);
    menu.setup();
}

function makeElement(whichEl,whichWidth,whichContainer) {
	if (NS4) {
		if (whichWidth) {
			elWidth = whichWidth;
		}
		else {
			elWidth = whichContainer.menuWidth - (borWid*2) - (itemPad*2);
		}
		if (!whichContainer) whichContainer = menuLoc;
		eval(whichEl + "= new Layer(elWidth,whichContainer)");
	}
	else {
		if (IE5) {
			newDiv                = menuLoc.document.createElement("DIV");
			newDiv.style.position = "absolute";
			newDiv.id             = whichEl;
			menuLoc.document.body.appendChild(newDiv);
		}
		else {
			elStr = "<DIV ID=" + whichEl + " STYLE='position:absolute'></DIV>";
			menuLoc.document.body.insertAdjacentHTML("BeforeEnd",elStr);
		}
	}
	return eval(whichEl);
}

function itemSetup(whichItem,whichArray) {
	this.onmouseover = itemOver;
	this.container   = (NS4) ? this.parentLayer : this.parentElement;

	arrayPointer  = ((whichItem-1)*2)+1;
	this.dispText = whichArray[arrayPointer];
	this.linkText = whichArray[arrayPointer + 1];

    if (this.dispText == "<hr>") {
      this.dispText = "<hr noshade size=1>";
      this.isSep    = true;
    }
    else {
      this.isSep = false;
    }

	if (this.linkText) {
		if (NS4) {
			this.captureEvents(Event.MOUSEUP)
			this.onmouseup = linkIt;
		}
		else {
			this.onclick      = linkIt;
			this.style.cursor = "hand";
		}
	}

	if (NS4) {
		htmStr = this.dispText;
        
        if (fntBold) htmStr = htmStr.bold();
        if (fntItal) htmStr = htmStr.italics();
        
        htmStr = "<FONT FACE='" + fntFam + "' POINT-SIZE=" + fntSiz + ">" + htmStr+ "</FONT>";
        
        this.htmStrOver = htmStr.fontcolor(this.container.menuFontOver);
        this.htmStr     = htmStr.fontcolor(this.container.menuFontColor);
        this.visibility = "inherit";
        this.bgColor    = this.container.menuBGColor;
        
        if (whichItem == 1) this.top = borWid + itemPad;
        else                this.top = this.prevItem.top + this.prevItem.clip.height + separator;
        
        this.left       = borWid + itemPad;
        this.clip.top   = this.clip.left = -itemPad;
        this.clip.right = this.container.menuWidth-(borWid*2)-itemPad;
        maxTxtWidth     = this.container.menuWidth-(borWid*2)-(itemPad*2);

        this.txtLyrOff = new Layer(maxTxtWidth,this);
        this.txtLyrOff.document.write(this.htmStr);
        this.txtLyrOff.document.close();
        this.txtLyrOff.visibility = "inherit";

        this.clip.bottom = this.txtLyrOff.document.height+itemPad;

        this.txtLyrOn = new Layer(maxTxtWidth,this);
        this.txtLyrOn.document.write(this.htmStrOver);
        this.txtLyrOn.document.close();
        this.txtLyrOn.visibility = "hide";

        this.dummyLyr             = new Layer(100,this);
        this.dummyLyr.left        = this.dummyLyr.top = -itemPad;
        this.dummyLyr.clip.width  = this.clip.width;
        this.dummyLyr.clip.height = this.clip.height;
        this.dummyLyr.visibility  = "inherit";
	}
	else {
		with (this.style) {
			if(!IE5) {
				fontSize   = fntSiz + "pt";
				fontWeight = (fntBold) ? "bold"   : "normal";
				fontStyle  = (fntItal) ? "italic" : "normal";
				fontFamily = fntFam;
				padding    = itemPad;

				borderBottomWidth = separator + "px";
				borderBottomStyle = "solid";
			}
			color             = this.container.menuFontColor;
			borderBottomColor = this.container.menuSeparatorCol;
			backgroundColor   = this.container.menuBGColor;
		}
	}
}   

function menuSetup() {
	this.onmouseover     = menuOver;
	this.onmouseout      = menuOut;
	this.showIt          = showIt;
	this.keepInWindow    = keepInWindow;
	this.hideTree        = hideTree
	this.isOn            = false;
	this.currentItem     = null;
	this.hideSelf        = hideSelf;
		
	if (NS4) {
		this.bgColor     = this.menuBorCol;
		this.fullHeight  = this.lastItem.top + this.lastItem.clip.bottom + borWid;
		this.clip.right  = this.menuWidth;
		this.clip.bottom = this.fullHeight;
	}
	else {
		with (this.style) {
			width       = this.menuWidth;
			borderWidth = borWid;
			borderColor = this.menuBorCol;
			borderStyle = borSty;
			zIndex      = topZ;
		}
		this.lastItem.style.border      = "";
		this.fullHeight                 = this.offsetHeight;
		if(isMac)this.style.pixelHeight = this.fullHeight;
		this.fullHeight                 = this.scrollHeight;
		this.showIt(false);
		this.onselectstart              = cancelSelect;
		this.moveTo                     = moveTo;
		this.moveTo(0,0);
	}
}

function popUp(menuName,e){
	if (NS4 && NSresized) startIt();
	if (!isLoaded) return;

    linkEl         = (NS4) ? e.target : event.srcElement;
	linkEl.onclick = popMenu;
	
    if (!beingCreated && !areCreated) startIt();
	linkEl.menuName = menuName;   
}

function popMenu(e){
	if (!isLoaded || !areCreated) return true;

	eType = (NS4) ? e.type : event.type;
	if (eType != "click") return true;

	linkEl      = (NS4) ? e.target : event.srcElement;
	currentMenu = eval(linkEl.menuName);
	
	if (IE4) menuLocBod = menuLoc.document.body;

    xPos = (currentMenu.menuLeft) ? currentMenu.menuLeft : (NS4) ? (e.pageX + deltaX) : (event.clientX + menuLocBod.scrollLeft + deltaX);
	yPos = (currentMenu.menuTop)  ? currentMenu.menuTop  : (NS4) ? (e.pageY + deltaY) : (event.clientY + menuLocBod.scrollTop + deltaY);
	
    currentMenu.moveTo(xPos,yPos);
	currentMenu.keepInWindow()
	currentMenu.isOn = true;
	currentMenu.showIt(true);
    setGlobals();
	return false;
}

function menuOver(e) {
	this.isOn   = true;
	isOverMenu  = true;
	currentMenu = this;
}

function menuOut() {
	if (IE4) {
		theEvent = menuLoc.event;
		if (theEvent.srcElement.contains(theEvent.toElement)) return;
	}
	this.isOn      = false;
	isOverMenu     = false;
	menuLoc.status = "";
}

function itemOver(){
    if (this.container.currentItem && this.container.currentItem != this) {
        if (NS4) {
            this.container.currentItem.bgColor              = this.container.menuBGColor;
            this.container.currentItem.txtLyrOff.visibility = "inherit";
            this.container.currentItem.txtLyrOn.visibility  = "hide";
        }
        else {
            with (this.container.currentItem.style) {
                backgroundColor = this.container.menuBGColor;
                color           = this.container.menuFontColor;
            }
        }
    }

    if (!this.isSep) {
        if (IE4) {
            this.style.backgroundColor = this.container.menuBGOver;
            this.style.color           = this.container.menuFontOver;
        }
        else {
            this.bgColor               = this.container.menuBGOver;
            this.txtLyrOff.visibility  = "hide";
            this.txtLyrOn.visibility   = "inherit";
        }
        menuLoc.status                 = this.dispText;
    }
    else {
        menuLoc.status                 = "";
    }

	this.container.currentItem = this;
}

function moveTo(xPos,yPos) {
	this.style.pixelLeft = xPos;
	this.style.pixelTop  = yPos;
}

function showIt(on) {
	if (NS4) {
		this.visibility = (on) ? "show" : "hide";
		if (this.currentItem) {
			this.currentItem.bgColor              = this.menuBGColor;
			this.currentItem.txtLyrOff.visibility = "inherit";
			this.currentItem.txtLyrOn.visibility  = "hide";
		}
	}
	else {
		this.style.visibility = (on) ? "visible" : "hidden";
		if (this.currentItem) {
			with (this.currentItem.style) {
				backgroundColor = this.menuBGColor;
				color           = this.menuFontColor;
			}
		}
	}
	this.currentItem = null;
}

function keepInWindow() {
	rtScrBar = botScrBar = scrBars = 20;

	if (NS4) {
		winRight = (menuLoc.pageXOffset + menuLoc.innerWidth) - rtScrBar;
		rightPos = this.left + this.menuWidth;
	
		if (rightPos > winRight) {
            dif = rightPos - winRight;
            this.left -= dif;
		}

		winBot = (menuLoc.pageYOffset + menuLoc.innerHeight) - botScrBar ;
		botPos = this.top + this.fullHeight;

		if (botPos > winBot) {
			dif = botPos - winBot;
			this.top -= dif;
		}
		
		winLeft = menuLoc.pageXOffset;
		leftPos = this.left;

		if (leftPos < winLeft) this.left = 5;
	}
	else {
		winRight = (menuLoc.document.body.scrollLeft + menuLoc.document.body.clientWidth) - rtScrBar;
		rightPos = this.style.pixelLeft + this.menuWidth;
	
		if (rightPos > winRight) {
            dif = rightPos - winRight;
            this.style.pixelLeft -= dif;
		}

		winBot = (menuLoc.document.body.scrollTop + menuLoc.document.body.clientHeight) - botScrBar;
		botPos = this.style.pixelTop + this.fullHeight;

		if (botPos > winBot) {
			dif = botPos - winBot;
			this.style.pixelTop -= dif;
		}
		
		winLeft = menuLoc.document.body.scrollLeft;
		leftPos = this.style.pixelLeft;

		if (leftPos < winLeft) this.style.pixelLeft = 5;
	}
}

function linkIt() {
	if (this.linkText.indexOf("javascript:")!=-1) eval(this.linkText)
	else menuLoc.location.href = this.linkText;
}

function popDown(menuName){
	if (!isLoaded || !areCreated) return;
	whichEl      = eval(menuName);
	whichEl.isOn = false;
}

function hideTree() { 
	if (!isOverMenu) this.hideSelf();
}

function hideSelf() {
	if (!this.isOn && !isOverMenu) this.showIt(false);
}

function cancelSelect(){return false}

function reDo(){
	if (window.innerWidth == origWidth && window.innerHeight == origHeight) return;
	initVars();
	NSresized = true;
	menuLoc.location.reload();
}

function clicked() {
	if (!isOverMenu && currentMenu != null && !currentMenu.isOn) currentMenu.hideTree();
}

function hidepopups() {
 popDown('elMenu1');
 popDown('elMenu2');
 popDown('elMenu3');
}

function setGlobals() {
  gFile  = cFile;
  gRitem = cRitem;
}

function showpopup(item,ritem,id,df,e) {
   cFile  = item;
   cRitem = ritem;

 popup = (df == "file") ? "elMenu1" : ((df == "dir") ? "elMenu2" : "elMenu3");
 popUp(popup,e);
}

window.onerror = handleErr;

function handleErr(){
	arAccessErrors = ["permission","access"];
	mess = arguments[0].toLowerCase();
	found = false;
	for (i=0;i<arAccessErrors.length;i++) {
		errStr = arAccessErrors[i];
		if (mess.indexOf(errStr)!=-1) found = true;
	}
	return found;
}
