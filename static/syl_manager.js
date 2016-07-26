
var EMAIL_RECIPIENTS_EDIT = [];
var EMAIL_RECIPIENTS = [];

function shareSylInfo(){
				document.getElementById("syl_status_box").style.visibility = "visible";	
			}
function hideStatBox(){
	document.getElementById("syl_status_box").style.visibility = "hidden";	
}

function submitClick(btnName){
	document.show_hide_form.btnName.click();	
}

function showOptionMenu(){
	var curElem = document.getElementById("option_menu");
	/*curElem.style.display = "block";*/
	curElem.style.width = '20%';
	document.getElementById("options").style.display = "none";	
}
function hideOptionMenu(){
	var curElem = document.getElementById("option_menu");
	/*curElem.style.display = "none";*/
	curElem.style.width = "0%";
	document.getElementById("options").style.display = "inline";	

}
function showEmailWindow(divID){
	var curDiv = document.getElementById(divID);
	curDiv.style.display = "block";
	hideOptionMenu();
	document.getElementById("blackout").style.display = "block";
}
function closeEmail(divID){
	var cancelBool = confirm("Closing this window will discard all changes. Do you wish to continue?");
	if (cancelBool){
		var curDiv = document.getElementById(divID);
		curDiv.style.display = "none";
		document.getElementById("blackout").style.display = "none";
	}
	restoreRecipientList();
}

function restoreRecipientList(){
	for (var i = 0; i < EMAIL_RECIPIENTS.length; i++){
		var curElem = EMAIL_RECIPIENTS[i];
		if (EMAIL_RECIPIENTS_EDIT.indexOf(curElem) == -1){
			EMAIL_RECIPIENTS_EDIT.push(curElem);
			formatRecipient(curElem);
		}	
	}
	EMAIL_RECIPIENTS_EDIT = EMAIL_RECIPIENTS;
}

/*MODEL*/
/*<span class="email_recipient" id="{{i}}_span"><span class="email_rec_span" style="display:inline-block;" id="{{i}}">{{i}}</span><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/VisualEditor_-_Icon_-_Close.svg/1000px-VisualEditor_-_Icon_-_Close.svg.png" style="cursor:pointer;" class="close_recipient" onclick="deleteRecipient('{{i}}_span')"/></span>*/

function formatRecipient(recipient){
	var curElem = document.createElement("SPAN");
	curElem.className = "email_recipient";
	curElem.id = recipient + "_span";
	
	var curSpan = document.createElement("SPAN");
	curSpan.className = "email_rec_span";
	curSpan.style.display = "inline-block";
	curSpan.id = recipient;
	
	var curText = document.createTextNode(recipient);
	curSpan.appendChild(curText);
	curElem.appendChild(curSpan);
	
	var curImg = document.createElement("IMG");
	curImg.src = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/VisualEditor_-_Icon_-_Close.svg/1000px-VisualEditor_-_Icon_-_Close.svg.png";
	curImg.style.cursor = "pointer";
	curImg.className = "close_recipient";
	curImg.onclick = function(){
		deleteRecipient(curElem.id);
	};
	curElem.appendChild(curImg);
	
	document.getElementById('hidden_rec_lst_syl').appendChild(curElem);
}

function formatRecipQuery(){	
	var qryStr = "";
	var len = EMAIL_RECIPIENTS_EDIT.length;
	var lastIndex = len - 1;
	for (var i = 0; i < len; i++){
		qryStr += EMAIL_RECIPIENTS_EDIT[i] + ",";	
		if (i == lastIndex){
			qryStr += EMAIL_RECIPIENTS_EDIT[i];	
		}
	}	
	return qryStr;
}
function sendEmail(){
	
	var submitBtnRec = document.getElementById('send_email');
	var submitBtnMsg = document.getElementById('send_email_msg');
	var message = document.getElementById('default_email').innerHTML;
	var recipient_qry = formatRecipQuery();
	
	submitBtnMsg.value = message;
	submitBtnRec.value = recipient_qry;
	submitBtnRec.click();
	restoreRecipientList();	
	window.alert("success!");
}

function autoClick(btnID){
	document.getElementById(btnID).click();	
}

function toggleSylOwners(show, field){
	var depsWSyl = document.getElementsByClassName("has_syllabus_" + field);
	if (show){
		for (var i = 0; i < depsWSyl.length; i++){
			depsWSyl[i].style.display = "inline";	
		}
	}
	else{
		for (var i = 0; i < depsWSyl.length; i++){
			depsWSyl[i].style.display = "none";	
		}
	}
}

function showDepsBtn(){
	var onDep = document.getElementById("dep_btn_submit_ID").value;
	var btn = document.getElementById("show_deps");
	if (onDep == "False"){
		btn.innerHTML = "Show All Departments<br><br>";
		btn.style.backgroundColor = "#990000";
		btn.style.color = "white";
		btn.style.border = "1px solid #990000";
		toggleSylOwners(false, "dep");
		/*window.alert("Setting value to True");
		window.alert("Whole input: " + document.getElementById("dep_btn_submit_ID"));*/
		document.getElementById("dep_btn_submit_ID").value = "True";
	}
	else{
		btn.innerHTML = "Show Only Departments with Missing Syllabi";
		btn.style.border = "1px solid #cccccc";
		btn.style.backgroundColor = "#cccccc";
		btn.style.color = "black";
		toggleSylOwners(true, "dep");
		/*window.alert("Setting value back to False");*/
		document.getElementById("dep_btn_submit_ID").value = "False";
	}
	/*window.alert("Current Value: " + document.getElementById("dep_btn_submit_ID").value);
	window.alert("Whole input: " + document.getElementById("dep_btn_submit_ID"));*/
}

function showProfsBtn(){
	var onProf = document.getElementById("prof_btn_submit_ID").value;
	var btn = document.getElementById("show_profs");
	if (onProf == "False"){
		btn.innerHTML = "Show All Professors in Chosen Department<br><br>";
		btn.style.backgroundColor = "#990000";
		btn.style.color = "white";
		btn.style.border = "1px solid #990000";
		toggleSylOwners(false, "prof");
		document.getElementById("prof_btn_submit_ID").value = "True";
	}
	else{
		btn.innerHTML = "Show Only Professors with Missing Syllabi in Chosen Department";
		btn.style.border = "1px solid #cccccc";
		btn.style.backgroundColor = "#cccccc";
		btn.style.color = "black";
		toggleSylOwners(true, "prof");
		document.getElementById("prof_btn_submit_ID").value = "False";
	}
}
function showTooltip(tooltipID){
	var tooltip = document.getElementById(tooltipID);
	tooltip.style.display = "inline-block";
	var notAvail = tooltip.parentElement;
	notAvail.style.color = "#6666ff";
	notAvail.style.cursor = "pointer";
	tooltip.style.color = "black";
}
function hideTooltip(tooltipID){
	var tooltip = document.getElementById(tooltipID);
	tooltip.style.display = "none";	
	var notAvail = tooltip.parentElement;
	notAvail.style.color = "black";
	notAvail.style.cursor = "pointer";
}


function showIndEmail(profName){
	showEmailWindow("ind_email");
	document.getElementById("send_to_input_box_ind").innerHTML = profName;
}


function findCurrentDate(){
	var curDate = new Date();
	var formattedDate = "";
	
	var curYear = curDate.getFullYear();
	formattedDate += curYear;
	var curMonth = curDate.getMonth();
	if (curMonth > 4){
		formattedDate += "01";	
	}
	else{
		formattedDate += "02";	
	}
}
/*MODEL*/
/*<span class="email_recipient"><span style="display:inline-block;">Alexander-Lee, Ashley </span><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/VisualEditor_-_Icon_-_Close.svg/1000px-VisualEditor_-_Icon_-_Close.svg.png" class="close_recipient" onclick="closeRecipient()"/></span>*/
function formatRecipients(){
	document.getElementById('hidden_rec_lst_syl').style.display = 'block';
	var curDiv = document.getElementById("hidden_rec_lst_syl");
	var recipientElems = document.getElementsByClassName("no_syllabus_prof");
	for (var i = 0; i < recipientElems.length; i++){
		var curSpan = document.createElement("SPAN");
		curSpan.className = "email_recipient";
		
		var curSpan2 = document.createElement("SPAN");
		curSpan2.style.display = "inline-block";
		
		var curText = document.createTextNode(recipientElems[i].id);
		var curImg = document.createElement("IMG");
		curImg.src = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/VisualEditor_-_Icon_-_Close.svg/1000px-VisualEditor_-_Icon_-_Close.svg.png";
		curImg.className = "close_recipient";
		
		curSpan2.appendChild(curText);
		curSpan2.appendChild(curImg);
		
		curSpan.appendChild(curSpan2);
		curDiv.appendChild(curSpan);
	}
}

function showRecipients(){
	var clicked = document.getElementById('hidden_rec_lst_syl').style.display === 'block';
	if (clicked){
		document.getElementById('hidden_rec_lst_syl').style.display = 'none';
		document.getElementById('search_recip').style.display = 'none';
	}
	else{
		document.getElementById('hidden_rec_lst_syl').style.display = 'block';
		document.getElementById('search_recip').style.display = 'block';
	}
}

function filterRecip(){
	var profs = document.getElementsByClassName("email_rec_span");
	var curInput = document.getElementById("search_recip").value.toLowerCase();
	var inputLen = curInput.length;
	
	var i;
	for (i = 0; i < profs.length; i++){
		var curElem = profs[i];
		var curSubStr = curElem.id.substring(0,inputLen).toLowerCase();
		
		if (curSubStr !== curInput){
			curElem.parentElement.style.display = "none";	
		}	
		else{
			curElem.parentElement.style.display = "inline-block";	
		}
	}
}
function deleteRecipient(spanID){
	var parent = document.getElementById("hidden_rec_lst_syl");
	var child = document.getElementById(spanID);
	parent.removeChild(child);
	
	var profNameLen = spanID.length - 5;
	var profName = spanID.substring(0, profNameLen);
	
	var i = EMAIL_RECIPIENTS_EDIT.indexOf(profName);
	if (i != -1){
		EMAIL_RECIPIENTS_EDIT.splice(i, 1);
	}
}

function animateChoice(bubble){
	
	if (bubble.style.color == "white"){
		alreadyAnimated = true;	
	}
	bubble.style.backgroundColor = "#003566";
	bubble.style.color = "white";
	bubble.style.border = "1px solid #4d4d4d";
	bubble.style.boxShadow = "3px 3px 10px #4d4d4d";
}

var alreadyAnimated = false;

function unAnimateChoice(bubble){
	
	if (!alreadyAnimated){
		bubble.style.backgroundColor = "#cce6ff";
		bubble.style.color = "black";
		bubble.style.border = "1px solid gray";
		bubble.style.boxShadow = "0px 0px 0px gray";
	}
	alreadyAnimated = false;
}

function filterDeps(){
	
	var deps = document.getElementsByClassName('dep_li');
	var input = document.getElementById('dep_search_bar').value;
	var inputLen = input.length;
	
	for (var i = 0; i < deps.length; i++){
		if ((deps[i].value.substring(0,inputLen)).toLowerCase() != input.toLowerCase()){
			deps[i].style.display = 'none';
		}
		else{
			deps[i].style.display = 'inline';	
		}	
	}	
}

function closeQuickInfo(quickInfo){
	quickInfo.parentElement.style.display = 'none';
	document.getElementById('main_body').style.height = '89%';
	document.getElementById('main_body').style.marginTop = '20px';
	document.getElementById('dept_search').style.height = '640px';
	document.getElementById('dept_search').style.top = '100px';
	document.getElementById('prof_search_container').style.height = '640px';
	document.getElementById('prof_search_container').style.top = '100px';
	document.getElementById('syl_status_box').style.marginTop = '15px';
	document.getElementById('syl_status_box').style.height = '640px';
	document.getElementById('prof_search').style.height = '570px';
}
