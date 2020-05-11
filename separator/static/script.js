class CommandStore {
	/*
	 * Stores all the augmentation input
	 * from the user.
	 */

	//Stores all commands untill submitted
	static customStorage = {};
	//Stores the session name
	static sessionName;
	//Stores wavesurfer object, used for reloading wave
	static cacheWave = {};
	//Store changed signal name, for reloading the original
	//version of signal
	static changedSignalName = [];

	static addCommand(name, jsonObject) {
		/*
		 * Add command to storage.
		 * Storage will be submitted to flask
		 * server when user clicks on augment.
		 */
		var commandName = jsonObject["commandName"]
		var keyValue = jsonObject[name]
		this.appendStorage(name, commandName, keyValue);
	}

	static initStorage(name) {
		/*
		 * Initialize key with signal names.
		 */
		this.customStorage[name] = {};
	}

	static reloadStorage(changedSignalName) {
		for(var key of changedSignalName) {
			this.customStorage[key] = {};
		}
		this.changedSignalName = changedSignalName
	}

	static reloadChangedSignalName() {
		this.changedSignalName = [];
	}

	static setObject(driverObject, key, value) {
		driverObject.setItem(key, value);
	}

	static getObject(driverObject, key) {
		if (typeof driverObject.getItem === "function" && typeof driverObject.getItem(key) != "undefined") {
			return driverObject.getItem(key);
		} else if(typeof driverObject[key] != "undefined") {
			return driverObject[key];
		}
		return null;
	}

	static appendStorage(name, commandName, keyValue) {
		var nameList = this.getObject(this.customStorage, name);
		var commandList = this.getObject(nameList, commandName);

		if (commandList == null) {
			commandList = [];
		}

		commandList.push(keyValue);
		this.customStorage[name][commandName] = commandList;
	}

	static getCommandDetails(name) {
		/*
		 * Get all command details for one
		 * type of signal provided by name.
		 */
		if(typeof this.customStorage[name] == "undefined") {
			return null;
		}

		var commands = this.customStorage[name];
		return commands;
	}

	static removeAugmentation(name, cmdName, idx) {
		/*
		 * Remove augmentation from `name` stem,
		 * `cmdName` command at the `idx` index
		 */
		if(this.customStorage[name] === null ||
		this.customStorage[name][cmdName] === null ||
		this.customStorage[name][cmdName].length <= idx) {
			return;
		}
		this.customStorage[name][cmdName].splice(idx, 1);
	}

	static updatedSignalNames() {
		var keys = [];
		for(var key in this.customStorage) {
			var commands = this.customStorage[key];
			var exists = false;
			for(var cmdName in commands) {
				if(commands[cmdName].length != 0) {
					exists = true;
					break;
				}
			}
			if(exists) {
				keys.push(key);
			}
		}
		console.log(keys);
		return keys;
	}

	static storeSessionName(sessionName) {
		this.sessionName = sessionName;
	}

	static storeWavesurfer(name, wavesurfer) {
		this.cacheWave[name] = wavesurfer;
	}

	static getWavesurfer(name) {
		return this.cacheWave[name];
	}

}

function printStorage() {
	/*
	 * Console command to print storage
	 */
	return CommandStore.customStorage;
}

class Command {
	/*
	 * This class deals with retrieval of user
	 * inputs and storing them as object
	 */
	constructor(wavesurfer, audioName) {
		this.wavesurfer = wavesurfer;
		this.audioName = audioName;
		this.getCommandName();
	}

	getCommandName() {
		//get current command selected
		this.commandForm = document.querySelector(".augment-form-nest-input.form-visible[id$="+this.audioName+"]");
		var commandTokens = this.commandForm.getAttribute("id").split('-');

		//format == (id=augment-{cmdName}-input-{audioName})
		this.commandName = commandTokens[1];

		//after knowing the command, get all relevant attributes accordingly
		this.command = this.getCommand();
	}

	getCommand() {
		/*
		 * Based on the command name
		 * create object of the specific
		 * command
		 */
		if(this.commandName === "vol") {
			//Volume
			return new Volume(this.getVolumeAttributes());
		} else if(this.commandName === "cop") {
			//Copy
			return new Copy(this.getCopyAttributes());
		}
	}

	getVolumeAttributes() {
		/*
		 * Get volume augmentation input
		 */
		var form = document.querySelector("#form-"+this.audioName)
		var newVolume = document.querySelector("#vol-input-slider-"+this.audioName).value;
		var newStart = form.elements["start-"+this.audioName].value;
		var newEnd = form.elements["end-"+this.audioName].value;

		return {start: newStart, end: newEnd, volume: newVolume}
	}

	getCopyAttributes() {
		/*
		 * Get copy augmentation input
		 */
		var oldStart = Number(document.querySelector("#start-"+this.audioName).value);
		var oldEnd = Number(document.querySelector("#end-"+this.audioName).value);
		var copyStart = Number(document.querySelector("#cop-start-"+this.audioName).value);

		var copyEnd = copyStart + oldEnd - oldStart
		this.wavesurfer.regions.add(this.wavesurfer.addRegion({
			start: copyStart,
			end: copyEnd,
			drag: false,
			resize: false,
			color: getCopyColor()
		}));

		return {start: oldStart, end: oldEnd, copyStart: copyStart}
	}

	/*
	 * Add custom getCmdAttributes <here>
	 */

	getObject() {
		var jsonObject = {};
		jsonObject[this.audioName] = this.command;
		jsonObject["commandName"] = this.command.name;
		return jsonObject;
	}
}

class Volume {
	start;
	end;
	volume;
	name="Volume";

	constructor(attr) {
		this.start = attr["start"];
		this.end = attr["end"];
		this.volume = attr["volume"];
	}

	static pretty(obj) {
		return {
			"Command Name": obj.name,
			"Start Timestamp": obj.start,
			"End Timestamp": obj.end,
			"Target Volume": obj.volume + "%"
		};
	}
}

class Copy {
	start;
	end;
	copyStart;
	name="Copy";

	constructor(attr) {
		this.start = attr["start"];
		this.end = attr["end"];
		this.copyStart = attr["copyStart"];
	}

	static pretty(obj) {
		return {
			"Command Name": obj.name,
			"Start Timestamp": obj.start,
			"End Timestamp": obj.end,
			"New Copy Timestamp": obj.copyStart
		};
	}
}

function loadWave(dir, name, augmented) {

	var wavesurfer = CommandStore.getWavesurfer(name);
	if(wavesurfer == null) {
		wavesurfer = WaveSurfer.create({
			container: "#waveform-" + name,
			plugins: [WaveSurfer.regions.create({
				regions: [
					{
						start: 1,
						end: 3,
						color: 'hsla(400, 100%, 30%, 0.5)',
					}
				],
				dragSelection: {
					slop: 5
				}
			}), WaveSurfer.timeline.create({
					container: '#wave-timeline-' + name
				})]
			});
	}

	//Load the waveform
	if(augmented) {
		wavesurfer.load(`http://192.168.0.107:5000${dir}/augmented/${name}.wav`);
	} else {
		wavesurfer.load(`http://192.168.0.107:5000${dir}/${name}.wav`);
	}

	return wavesurfer;
}

document.addEventListener("DOMContentLoaded", function() {
	//Initialize all listeners
	addListeners();

	var waves = document.getElementsByClassName("waveform")
	for (wav of waves) {
		//For each waveform setup the page
		name = wav.getAttribute("name");
		dir = wav.getAttribute("dir");

		var wavesurfer = loadWave(dir, name, false);

		//Object specific listeners
		setValues(wavesurfer, name);
		//Initialize storage for particular signal
		CommandStore.initStorage(name);
		CommandStore.storeSessionName(dir);
		CommandStore.storeWavesurfer(name, wavesurfer);

	}
});

function setValues(wavesurfer, name) {

	setPlayButton(wavesurfer, name);

	//Whenever a region is clicked show the form
	wavesurfer.on("region-click", region => {editAnnotation(region, name)});
	wavesurfer.on("region-update-end", region => {editAnnotation(region, name)});

	//Whenever user clicks on add button, store the user input.
	var addCommandButton = document.querySelector("#add-command-"+name);
	addCommandButton.onclick = function() {
		commandListener(wavesurfer, name);
	}

	//Add progress bar before audio is fully loaded
	progressBar(wavesurfer, name);
}

function setPlayButton(wavesurfer, name) {
	/*
	 * Listeners for audio playback across the page
	 */
	document.querySelector("#button-" + name).onclick = (function(surf) {
						return function() {surf.playPause()}
						})(wavesurfer);

	document.querySelector("#button-forward-" + name).onclick = (function(surf) {
						return function() {surf.skipForward()}
						})(wavesurfer);

	document.querySelector("#button-backward-" + name).onclick = (function(surf) {
						return function() {surf.skipBackward()}
						})(wavesurfer);

	document.querySelector("#button-stop-" + name).onclick = (function(surf) {
						return function() {surf.stop()}
						})(wavesurfer);

	document.querySelector("#slider-"+name).oninput = (function(surf) {
						return function() {surf.zoom(this.value);}
						})(wavesurfer);

	document.querySelector("#play-all").onclick = function() {
		document.querySelectorAll(".button-play-wave").forEach(btn => {btn.click()})
	};

	document.querySelector("#stop-all").onclick = function() {
		document.querySelectorAll(".button-stop-wave").forEach(btn => {btn.click()})
	};

	document.querySelector("#play-forward-all").onclick = function() {
		document.querySelectorAll(".button-forward-wave").forEach(btn => {btn.click()})
	};

	document.querySelector("#play-backward-all").onclick = function() {
		document.querySelectorAll(".button-backward-wave").forEach(btn => {btn.click()})
	};
}

function progressBar(wavesurfer, name) {
	var progressDiv = document.querySelector('#progress-bar-'+name);
	var progressBar = progressDiv.querySelector('.progress-bar');

	var showProgress = function(percent) {
		progressDiv.style.display = 'block';
		progressBar.style.width = percent + '%';
	};

	var hideProgress = function() {
		progressDiv.style.display = 'none';
	};

	wavesurfer.on('loading', showProgress);
	wavesurfer.on('ready', hideProgress);
	wavesurfer.on('destroy', hideProgress);
	wavesurfer.on('error', hideProgress);
}

function commandListener(wavesurfer, audioName) {
	var command = new Command(wavesurfer, audioName);
	var jsonCommand = command.getObject();
	console.log(jsonCommand);
	CommandStore.addCommand(audioName, jsonCommand);
}

function editAnnotation(region, name) {
	var form = document.querySelector("#form-"+name)
	form.classList.add("form-visible-flex");

	(form.elements["start-"+name].value = Math.round(region.start * 10) / 10),
	(form.elements["end-"+name].value = Math.round(region.end * 10) / 10);

	form.onsubmit = function(e) {
		newStart = form.elements["start-"+name].value
		newEnd = form.elements["end-"+name].value
		e.preventDefault();
		region.update({
			start: newStart,
			end: newEnd
		});
		form.classList.remove("form-visible-flex");
	};

	form.onreset = function() {
		form.style.opacity = 0;
		form.dataset.region = null;
	};

	form.dataset.region = region.id;
}

function addListeners() {
	/*
	 * Setup all listeners
	 */

	//Bulma is a pure CSS framework. Hence, custom JS to show file name when user
	//selects a file
	const fileInput = document.querySelector('#file-input-upload input[type=file]');
	if(fileInput != null) {
		fileInput.onchange = () => {
			if (fileInput.files.length > 0) {
				const fileName = document.querySelector('#file-input-upload .file-name');
				fileName.textContent = fileInput.files[0].name;
			}
		}
	}

	var volume_button = document.querySelector("#radio-Volume");
	var copy_button = document.querySelector("#radio-Copy");

	function enableAugment(form) {
		/*
		 * Toggle form based on user click
		 */
		document.querySelectorAll(".augment-form-nest-input").forEach(
			(item) => {item.classList.remove("form-visible")}
		);
		form.classList.add("form-visible");
	}

	var allAugmentInputs = document.querySelectorAll(".augment-input");
	for(augmentInput of allAugmentInputs) {
		augmentInput.onclick = (function(scopeAugment) {
			return function () {
			var curId = scopeAugment.getAttribute("id");
			tokens = curId.split('-')
			var name = tokens[tokens.length-1]

			var allButton = document.querySelectorAll("#"+curId+" .augment-radio");
			for(button of allButton) {
				button.onclick = (function(scopeButton) {
					return function() {
					var buttonText = scopeButton.getAttribute("id").split('-')[0];
					var cmd = buttonText.toLowerCase().slice(0, 3);
					var form = document.querySelector("#augment-"+cmd+"-input-"+name);

					enableAugment(form);
				}})(button);
			}
		}})(augmentInput);
	}

	var augmentButton = document.querySelector("#augment-final-button");
	if(augmentButton != null) {
		augmentButton.onclick = sendAugmentData;
	}

	var loadOriginalButton = document.querySelector("#reload-original");
	if(loadOriginalButton != null) {
		loadOriginalButton.onclick = function() {
			loadOriginal(this, CommandStore.changedSignalName);
		};
	}

	var uploadForm = document.querySelector("#upload-form");
	if(uploadForm != null) {
		uploadForm.onsubmit = function() {
			var uploadButton = document.querySelector("#upload-button");
			uploadButton.classList.add("hidden");

			var uploadBar = document.querySelector("#upload-bar");
			uploadBar.classList.remove("hidden");
		}
	}

	//Show modal
	var toggleButton = document.querySelectorAll(".toggle-modal[id^='toggle-modal']");
	toggleButton.forEach(t=> {
		var name = getLastItem(t.getAttribute("id").split('-'));
		t.onclick = function() {
			toggleModalClasses(name);
		};
	});

	var saveModalButton = document.querySelector("#toggle-modal-save");
	if(saveModalButton != null) {
		saveModalButton.onclick = function() {
			removeMarkedItems();
			toggleModalClasses(name);
		}
	}

}

function toggleModalClasses(name) {
	//Retrieve all user commands
	var modal = document.querySelector(".modal");

	var cmdDetails = CommandStore.getCommandDetails(name);
	if(cmdDetails === null) {
		cmdDetails = {}
	}
	addTablesToModal(cmdDetails, name);

	if(modal.classList.contains("is-active")) {
		modal.classList.remove('is-active');
	} else {
		modal.classList.add('is-active');
	}
}

function addTablesToModal(cmdDetails, name) {
	//Add table as a child to modal-body
	var modalBody = document.querySelector(".modal-card-body");
	modalBody.innerHTML = "";
	var subtitle = document.createElement("label");
	var subtitleText = name.charAt(0).toUpperCase() + name.substr(1);
	subtitle.innerHTML = subtitleText;

	var tables = [];
	for(cmdName in cmdDetails) {
		//Each iteration creates a table.
		var table = document.createElement("table");
		var cmd = cmdDetails[cmdName];
		if(cmd.length === 0) {
			continue;
		}

		var tableHead = document.createElement("thead");
		var headRow = document.createElement("tr");
		var prettyObj = getPrettyCommand(cmdName, cmd[0]);
		var tableSubtitleText;

		for(key in prettyObj) {
			if(key==="Command Name"){
				tableSubtitleText = prettyObj[key];
				continue;
			}
			var headData = document.createElement("th");
			headData.innerHTML = key;
			headRow.appendChild(headData);
		}
		tableHead.appendChild(headRow);
		table.appendChild(tableHead);

		//Add row
		var idx = 0;
		for(c of cmd) {
			prettyObj = getPrettyCommand(cmdName, c);
			var dataRow = document.createElement("tr");

			for(key in prettyObj) {
				if(key==="Command Name"){continue;}
				//Add column value
				var data = prettyObj[key];
				var rowEntry = document.createElement("td");

				rowEntry.innerHTML = data;
				dataRow.appendChild(rowEntry);
			}
			var buttonEntry = document.createElement("td");
			buttonEntry.className = "no-bottom-border";
			var markItemButton = document.createElement("button");
			markItemButton.className = "delete has-background-danger";

			markItemButton.onclick = (function(cId, cName) {
				return function() {return markItemListener(name, cName, cId);}
			})(idx, cmdName);

			buttonEntry.appendChild(markItemButton);
			dataRow.appendChild(buttonEntry);
			dataRow.setAttribute("id", `${name}-${cmdName}-${idx}`);
			table.appendChild(dataRow);
			idx += 1;
		}
		tables.push({table: table, subtitle: tableSubtitleText});
	}

	console.log(cmdDetails);
	if(cmdDetails.length === 0 || Object.keys(cmdDetails).length === 0 ||
		tables.length === 0) {
		var label = document.createElement("label");
		label.innerHTML = `No Augmentations for ${subtitleText}. Add augmentations by clicking on a region on the waveform`
		modalBody.appendChild(label);
	}

	for(tableWrap of tables) {
		var table = tableWrap["table"];
		subtitleText = tableWrap["subtitle"];

		subtitle = document.createElement("label");
		subtitle.innerHTML = subtitleText;

		table.className = "table";
		modalBody.appendChild(subtitle);
		modalBody.appendChild(table);
	}
}

function markItemListener(name, cmdName, idx) {
	console.log(name, cmdName, idx);
	var row = document.querySelector("#"+name+"-"+cmdName+"-"+idx);
	if(row.classList.contains("row-strikethrough")) {
		row.classList.remove("row-strikethrough");
	} else {
		row.classList.add("row-strikethrough");
	}
}

function removeMarkedItems() {
	var markedRow = document.querySelectorAll(".row-strikethrough");
	markedRow.forEach(mr => {
		var tokens = mr.getAttribute("id").split('-');
		CommandStore.removeAugmentation(tokens[0], tokens[1], tokens[2]);
	});
}

function getPrettyCommand(cmdName, cmd) {
	if(cmdName === "Copy") {
		return Copy.pretty(cmd);
	} else if(cmdName === "Volume") {
		return Volume.pretty(cmd);
	}
}

function getCopyColor() {
	color = "hsla(0, 0, " + Math.random() + ", 1)";
}

function sendAugmentData() {
	var augmentButton = document.querySelector("#augment-final-button");
	augmentButton.classList.add("is-loading");
	var xhr = new XMLHttpRequest();
	jsonData = JSON.stringify(CommandStore.customStorage);

	var changedSignalName = CommandStore.updatedSignalNames();

	xhr.open('POST', '/augmented');
	xhr.setRequestHeader('Content-Type', 'application/json');
	xhr.send(jsonData);

	xhr.onreadystatechange = function() {
		changedSignalName.forEach(c => {loadWave(CommandStore.sessionName, c, true)});
		augmentButton.classList.remove("is-loading");
		CommandStore.reloadStorage(changedSignalName);
	}
}

function loadOriginal(loadButton, signalNames) {
	loadButton.classList.add("is-loading");
	signalNames.forEach(c => {loadWave(CommandStore.sessionName, c, false)});
	loadButton.classList.remove("is-loading");

	CommandStore.reloadChangedSignalName();
}

function getLastItem(arr) {
	len = arr.length;
	return arr[len-1];
}

