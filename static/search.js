
/* Generic function that closes any pop-up message 

divID - string representing the id of the popup message that 
needs to be closed 
*/
function closeDiv(divID){
	var curDiv = document.getElementById(divID);
	curDiv.style.display = "none";
	document.getElementById("blackout").style.display = "none";
}

/* Opens and Closes the Accordion 

accContentID - a string representing the id of the accordion
content that the user wishes to hide/display 
*/
function toggleAcc(accContentID){
	var accContent = document.getElementById(accContentID);
	if (accContent.style.display == 'block'){
		accContent.style.display = 'none';
	}
	else{
		accContent.style.display = 'block';	
	}
}

/* Opens and closes the filter.
    To close the filter, you must give the div a negative margin to move
    it off the screen. The opposite occurs when opening the filter -- set the
    margin to 0.
    
closeFilter - a boolean that indicates whether the filter should be opened or 
closed 
*/
function toggleFilter(closeFilter){
	var filter = document.getElementById('filter');
	var menu = document.getElementById('menu-icon');
	var main = document.getElementById('main');
	if (closeFilter){
		/* The transition is begins slowly and then picks up speed, which means 
		the filter exits more slowly and enters more quickly. To look more uniform,
		must assign a quicker transition time to the exit function, etc.*/
		filter.style.transition = '2s'; 
		filter.style.marginLeft = '-1000px';	
		/* Must wait for filter to leave to display the menu icon */
		setTimeout(function(){menu.style.display = 'block';}, 400); 
		main.style.width = '100%';
		main.style.marginLeft = "0%";
		document.getElementById("help_div").style.left = '35%';
		document.getElementById('course_desc_div').style.left = '30%';
	}
	else{
		filter.style.transition = '0.7s';
		filter.style.marginLeft = '0px';
		/* Filter enters more quickly, but still need to wait */
		setTimeout(function(){menu.style.display = 'none';}, 300);
		main.style.width = '75%';
		main.style.marginLeft = "25%";
		document.getElementById("help_div").style.left = '48%';
		document.getElementById('course_desc_div').style.left = '43%';
	}	
}

/* hasClass function 

element - the HTML element that we wish to check for a particular class
clss - a string representing the classname that we wish to check 
*/
function hasClass(element, clss) {
	return (element.className).indexOf(clss) > -1;
}

/* Checks and Unchecks a checkbox -- for styling. Changes the color of the
text belonging to that checkbox when it is checked.

checkboxLabelID - a string representing the id of the label that belongs
to the checkbox being checked 
*/
function toggleCheckbox(checkboxLabelID){
	var checkboxLabel = document.getElementById(checkboxLabelID);
	var checkbox = document.getElementById(checkboxLabel.htmlFor);
	if (checkbox.checked){
		checkboxLabel.style.color = "#008080";
	}
	else{
		checkboxLabel.style.color = "black";
	}
}

/* Resets the filter, both checkboxes and selects (except the semester) */
function clearAll(){
	var checkboxLabels = document.getElementsByClassName('checkbox-label');	
	
	for (var i = 0; i < checkboxLabels.length; i++){
		var label = checkboxLabels[i];
		var checkbox = document.getElementById(label.htmlFor);
		label.style.color = 'black';
		checkbox.checked = false;	
	}

	document.getElementById('from-class-size-select').options[0].selected = true;
	var toSelect = document.getElementById('to-class-size-select');
	toSelect.options[toSelect.length - 1].selected = true;
}


/*------------------------Professor Oninput Filter Function----------------------*/
function filterProfs(){

	var profs = document.getElementsByClassName("prof");
	var curInput = document.getElementById("prof_search_id").value.toLowerCase();
	var inputLen = curInput.length;
	
	var i;
	for (i = 0; i < profs.length; i++){
		var curElem = profs[i];
		var curSubStr = curElem.value.substring(0,inputLen).toLowerCase();
	
		if (curSubStr !== curInput){
			curElem.parentElement.style.display = "none";	
		}	
		else{
			curElem.parentElement.style.display = "block";	
		}
	}
}

/* When the user clicks "Morning" or "Afternoon", checks the appropriate 
checkboxes. 

mornAftClassname - a string representing the classname for morning ('morn_check') 
or Afternoon ('aft_check') 
input - an HTML checkbox input element - will belong to "Morning" or "Afternoon"
*/
function toggleMornAft(mornAftClassname, input){
	var mornAftClasses = document.getElementsByClassName(mornAftClassname);
	var check = false;
	var color = 'black';
	
	if (input.checked){
		check = true;
		color = '#008080';
	}
	for (var i = 0; i < mornAftClasses.length; i++){
		mornAftClasses[i].checked = check;
		document.getElementById(mornAftClasses[i].id + '_label').style.color = color;
	}
}


/*Creates query to pass to the db -- takes values from the checkboxes and the select menus 
to assign them to hidden inputs which can be processed by the python code */

/* Each field will have its own query (profStr, deptStr, etc). If there are multiple values within a certain field, they are divided by " or ", which will be the split RegEx for the python file ('search.py').*/
function createQueryStr(){

	var profStr = "";
	var deptStr = "";
	var dayStr = "";
	var timeStr = "";
	var distStr = "";
	var semStr = "";
	var classSizeStr = "";
	
	var checkedBoxes = document.getElementsByClassName("choices");
	for(var i = 0; i < checkedBoxes.length; i++){
		var curElem = checkedBoxes[i];
		if (curElem.checked){
			if (hasClass(curElem, "prof_check")){
				var replacemt;
				if(profStr != ""){
					replacemt = profStr.concat(" or ", curElem.value);
				}
				else{
					replacemt = profStr.concat(curElem.value);
	
				}
				profStr = replacemt;
			}
			if (hasClass(curElem, "dept_check")){
				var replacemt;
				if(deptStr != ""){
					replacemt = deptStr.concat(" or ", curElem.value);
				}
				else{
					replacemt = deptStr.concat(curElem.value);
				}
				deptStr = replacemt;
			}
			if (hasClass(curElem,"day_check")){
				var replacemt;
				if(dayStr != ""){
					replacemt = dayStr.concat(" or ", curElem.value);
				}
				else{
					replacemt = dayStr.concat(curElem.value);
				
				}
				dayStr = replacemt;
			}
			if (hasClass(curElem,"time_check")){
				var replacemt;
				if(timeStr != ""){
					replacemt = timeStr.concat(" or ", curElem.value);
				}
				else{
					replacemt = timeStr.concat(curElem.value);
				
				}
				timeStr = replacemt;
			}
			if (hasClass(curElem,"dist_req_check")){
				var replacemt;
				if(distStr != ""){
					replacemt = distStr.concat(" or ", curElem.value);
				}
				else{
					replacemt = distStr.concat(curElem.value);
				
				}
				distStr = replacemt;
			}
		}
	}
	
	/* Class size query format: '0-6' or '12-36' 
	  '-' is the RegEx for the python script */
	var fromClassSize = document.getElementById('from-class-size-select');
	var fromAns = (fromClassSize.options[fromClassSize.selectedIndex]).innerHTML;
	var toClassSize = document.getElementById('to-class-size-select');
	var toAns = (toClassSize.options[toClassSize.selectedIndex]).innerHTML;
	/* If default values, don't bother passing to the python script */
	/* May need fixing -- '56' (the max) is subject to change by semester*/
	if ((fromAns == "1") && (toAns == "56")){ 
		classSizeStr = "";
	}
	else{
		classSizeStr = fromAns + "-" + toAns;	
	}
	
	var semDropdown = document.getElementById("year_dropdwn");
	var semChoices = semDropdown.options;
	var semAns = semChoices[semDropdown.selectedIndex];
	var replacemt;
	replacemt = semStr.concat(semAns.value);
	semStr = replacemt;
	
	document.getElementById("period").value = semStr;
	document.getElementById("prof_form").value = profStr;
	document.getElementById("dep").value = deptStr;
	document.getElementById("days").value = dayStr;
	document.getElementById("times").value = timeStr;
	document.getElementById("distri").value = distStr; 	
	document.getElementById("class_size").value = classSizeStr;	
}


/* Displays the iframe with the course description

divID - a string representing the id of the div that will contain the iframe
dept - a string representing the department the course belongs to (for the link)
course_num - a string representing the course number (for the link) 
*/
function showDescription(divID, dept, course_num){

	var curDiv = document.getElementById(divID);
	curDiv.style.display = "block";
	document.getElementById("blackout").style.display = "block"; 	
	
	curDiv.style.marginTop = "10%";
	var limitingDiv = document.createElement("DIV");
	limitingDiv.id = "iframe_sur_div";
	limitingDiv.style.padding = "0px";
	limitingDiv.style.boxShadow = "0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 8px 20px 0 rgba(0, 0, 0, 0.19)";
	limitingDiv.style.overflow = "hidden";
	var a = document.createElement('iframe');
	a.id = "iframe_description"
	a.src = "http://www.davidson.edu/general-course-detail/?subj=" + dept + "&cnum=" + course_num;	
	a.width = "100%";
	a.height = "1410";
	/* Use negative margins and a wrapping div (limitingDiv) to make the iframe display only 
	the course description, not the rest of the page. Not completely effective because of 
	page resizing */
	a.style.marginTop = "-180px";
	a.style.marginBottom = "-800px";
	a.frameborder = "1";
	limitingDiv.appendChild(a);
	
	var cancelBtn = document.getElementById('put_here');
	curDiv.insertBefore(limitingDiv, cancelBtn);
}

/* Used to close the iframe description window 
      Completely removes the iframe inside the div so a new 
      iframe can be displayed next time, then hides the div 
      
divID - string representing the id of the div that contains the iframe 
*/
function closeDescription(divID) {
	var descriptionElem = document.getElementById("iframe_sur_div");
	document.getElementById(divID).removeChild(descriptionElem);
	closeDiv(divID);
}

/* Opens or Closes all of the results accordions

open - a boolean that indicates whether to open or close all accordions
*/
function openCloseAllAccordions(open){
	var accContents = document.getElementsByClassName('acc-content-results');
	var display = 'none';
	if (open){
		display = 'block';	
	}
	for (var i = 0; i < accContents.length; i++){
		accContents[i].style.display = display;
	}
}

/* Changes how the Open/Close Accordions button looks and 
calls openCloseAllAccordions()*/
function toggleOpenCloseBtn(){
	var openCloseBtn = document.getElementById('open-close-btn');
	if (openCloseBtn.innerHTML == "Open All"){
		openCloseBtn.style.backgroundColor = "white";
		openCloseBtn.style.color = "#660000";
		openCloseBtn.innerHTML = "Close All";
		openCloseAllAccordions(true);
	}	
	else{
		openCloseBtn.style.backgroundColor = "#660000";
		openCloseBtn.style.color = "white";
		openCloseBtn.innerHTML = "Open All";
		openCloseAllAccordions(false);
	}
}

/* Hides (or displays) all accordions that are 
not 'visitable' by prospective students

visitable - a boolean that indicates whether the user wants 
or does not want to see the classes that you cannot visit 
*/
function visNoAllAccordions(visitable){
	var visContents = document.getElementsByClassName('visit-row');
	var nopeContents = document.getElementsByClassName('no-visit-row');
	console.log(visContents.length);
	console.log(nopeContents.length);
	display = 'block';
	if (visitable) {
		display = 'none';	
	}
	for (var j = 0; j < nopeContents.length; j++){					
		nopeContents[j].parentNode.style.display = display;	
	}
}

/* Changes how the Visitable button looks and calls visNoAllAccordions()*/
function toggleVisNoBtn() {
	var visNoBtn = document.getElementById('vis-no-btn');		
	if (visNoBtn.innerHTML == "Allow Visitors"){
		visNoBtn.style.backgroundColor = "white";
		visNoBtn.style.color = "#660000";
		visNoBtn.innerHTML = "No Visitors";
		visNoAllAccordions(true);
	}	
	else{
		visNoBtn.style.backgroundColor = "#660000";
		visNoBtn.style.color = "white";
		visNoBtn.innerHTML = "Allow Visitors";
		visNoAllAccordions(false);
	}
}

/* Displays tooltips for Department and Distribution Requirement filters. 
May choose the display type depending on the div. 
Use 'block' to display below; use 'inline' to display to the right.

tooltipID - string representing id for the tooltip
displayType - string representing the type of display, whether 'block' or 'inline'
*/
function showTooltip(tooltipID, displayType){
	document.getElementById(tooltipID).style.display = displayType;
}
/* Hides the tooltip 
tooltipID - string representing id for the tooltip
*/
function hideTooltip(tooltipID){
	document.getElementById(tooltipID).style.display = 'none';
}

/* After the homepage, there is a transition to display the results. This is that transition 

searchBox - an HTML element containing the search bar, button, and Help
*/ 
function mainPageSetup(searchBox){
	searchBox.style.marginTop = "5px";	
	searchBox.style.width = "90%";
	searchBox.style.margin = "0 auto";
	searchBox.style.height = "55px";
	searchBox.style.paddingTop = "0px";
	document.getElementById("by_keyword_home").style.position = "absolute";
	document.getElementById("search_bar").style.marginLeft = "180px";
	document.getElementById("search_bar").style.width = "calc(100% - 180px)";
	document.getElementById("search_home_td").style.width = "70%";
	document.getElementById("search_home").style.width = "99%";
	document.getElementById("search_btn_home_td").style.width = "5%";
	document.getElementById("help_td").style.display = 'block';
	document.getElementById("descript_page").style.display = "none";
	document.getElementById("open-close-btn").style.display = "inline";
	document.getElementById("vis-no-btn").style.display = "inline";
}

/* Display the results box after page load (Timeout is set so that
the page load does not affect the transition) */
function showResults(){
	setTimeout(function(){
		var searchBox = document.getElementById("opq_search_box");
		var results = document.getElementById("results");
	
		mainPageSetup(searchBox);
		
		/* Shows the results box */
		results.style.opacity = "1.0";
		results.style.zIndex = "0";
		results.style.position = "static";
	}, 10);
}

/* Sets up the page, then hides the results box (because there are no results)*/
function showNoResults(){
	setTimeout(function(){
		var searchBox = document.getElementById("opq_search_box");
		var results = document.getElementById("results");
		mainPageSetup(searchBox);
		
		results.style.opacity = "0.0";
		results.style.zIndex = "-1";
		results.style.position = "absolute";
	}, 10);
}

/* Select the user's semester even after reload 

semester - string representing the name of the semester 
*/
function keepSemester(semester){
	var yearInputs = document.getElementsByClassName("year_li");
	for(var x = 0; x < yearInputs.length; x++){
		var curElem = yearInputs[x];
		if(curElem.value == semester){
			curElem.selected = true;  
		}
	}	
}

/* Keeps the same class sizes after reload. 

class_size_kept - a string representing the string query that was 
passed off the the python script before reload 
*/
function keepClassSize(class_size_kept){
	var fromSelect = document.getElementById('from-class-size-select');
	var fromOptions = fromSelect.options;
	var toSelect = document.getElementById('to-class-size-select');
	var toOptions = toSelect.options;
	
	var split = class_size_kept.split("-");	
	var from = split[0];
	var to = split[1];
	
	var fromSolution;
	var foundSolFrom = false;
	for (var i = 0; i < fromOptions.length; i++){
		if (fromOptions[i].value == ("from_" + String(from))){
			fromSolution = fromOptions[i];
			foundSolFrom = true;
			break;	
		}
	}
	var toSolution = "";
	var foundSolTo = false;
	for (var i = 0; i < toOptions.length; i++){
		if (toOptions[i].value == ("to_" + String(to))){
			toSolution = toOptions[i];
			foundSolTo = true;
			break;	
		}	
	}
	
	if (foundSolTo && foundSolFrom){
		fromSolution.selected = true;
		toSolution.selected = true;	
		document.getElementById("class-size-acc-content").style.display = 'block';
	}	
}
