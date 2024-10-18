from burp import IBurpExtender, ITab, IContextMenuFactory
from javax.swing import JMenuItem, JPanel, JPasswordField, JTextField, JButton, JLabel, BoxLayout, JTextArea, Box, SwingConstants
from java.awt import Dimension, Font, Color, BorderLayout, GridBagLayout, GridBagConstraints, Insets
from java.awt.event import FocusListener
from javax.swing.border import EmptyBorder
from java.util import ArrayList
from java.net import URL
from java.io import PrintWriter, InputStreamReader, BufferedReader
from functools import partial
import json

class BurpExtender(IBurpExtender, ITab, IContextMenuFactory):
	def registerExtenderCallbacks(self, callbacks):
		self._callbacks = callbacks
		self._helpers = callbacks.getHelpers()
		self.stdout = PrintWriter(callbacks.getStdout(), True)
		self.stderr = PrintWriter(callbacks.getStderr(), True)

		callbacks.setExtensionName("BLACKBIRD Burpsuite Integration")
		callbacks.registerContextMenuFactory(self)

		# Create main panel
		self.mainPanel = JPanel()
		self.mainPanel.setLayout(BoxLayout(self.mainPanel, BoxLayout.Y_AXIS))
		self.mainPanel.setBorder(EmptyBorder(20, 30, 10, 0))  # Add padding to all sides

		# Title
		titleLabel = JLabel("BLACKBIRD Burpsuite Integration")
		titleLabel.setFont(Font(titleLabel.getFont().getName(), Font.BOLD, 24))
		titleLabel.setAlignmentX(JLabel.LEFT_ALIGNMENT)

		# Settings subtitle
		settingsLabel = JLabel("Configuration Settings")
		settingsLabel.setFont(Font(settingsLabel.getFont().getName(), Font.BOLD, 18))
		settingsLabel.setAlignmentX(JLabel.LEFT_ALIGNMENT)

		# API Key input and button panel
		SettingsPanel = JPanel(GridBagLayout())
		SettingsPanel.setAlignmentX(JPanel.LEFT_ALIGNMENT)

		gbc = GridBagConstraints()
		gbc.anchor = GridBagConstraints.WEST
		gbc.insets = Insets(2, 0, 5, 10)  # top, left, bottom, right padding

		self.APIKeyLabel = JLabel("API Key:", SwingConstants.LEFT)
		self.APIKeyLabel.setFont(Font(self.APIKeyLabel.getFont().getName(), Font.PLAIN, 16))

		self.APIKeyField = JPasswordField(20)
		self.APIKeyField.setMaximumSize(Dimension(450, 25))
		self.APIKeyField.setText("Enter your API key")
		self.APIKeyField.setForeground(Color.LIGHT_GRAY)  # Set initial text color to light gray
		self.APIKeyField.setCaretColor(Color.WHITE)  # Set cursor color to white
		self.APIKeyField.addFocusListener(self.PlaceholderFocusListener(self.APIKeyField, "Enter your API key"))

		# Timeout
		self.TimeoutLabel = JLabel("Timeout (ms):", SwingConstants.LEFT)
		self.TimeoutLabel.setFont(Font(self.TimeoutLabel.getFont().getName(), Font.PLAIN, 16))

		self.TimeoutField = JTextField(20)
		self.TimeoutField.setMaximumSize(Dimension(300, 25))
		self.TimeoutField.setText("Set a timeout in ms")
		self.TimeoutField.setForeground(Color.LIGHT_GRAY)  # Set initial text color to light gray
		self.TimeoutField.setCaretColor(Color.WHITE)  # Set cursor color to white
		self.TimeoutField.addFocusListener(self.PlaceholderFocusListener(self.TimeoutField, "Timeout (ms)"))


		# Delay
		self.DelayLabel = JLabel("Delay (ms):", SwingConstants.LEFT)
		self.DelayLabel.setFont(Font(self.TimeoutLabel.getFont().getName(), Font.PLAIN, 16))

		self.DelayField = JTextField(20)
		self.DelayField.setMaximumSize(Dimension(300, 25))
		self.DelayField.setText("Set a delay in ms")
		self.DelayField.setForeground(Color.LIGHT_GRAY)  # Set initial text color to light gray
		self.DelayField.setCaretColor(Color.WHITE)  # Set cursor color to white
		self.DelayField.addFocusListener(self.PlaceholderFocusListener(self.DelayField, "Delay (ms)"))

		# Save
		self.saveButton = JButton("Save", actionPerformed=self.saveSettings)
		self.saveButton.setMaximumSize(Dimension(120, 25))

		# API Key
		gbc.gridx = 0
		gbc.gridy = 0
		SettingsPanel.add(self.APIKeyLabel, gbc)

		gbc.gridx = 1
		gbc.gridy = 0
		gbc.fill = GridBagConstraints.HORIZONTAL
		gbc.weightx = 1.0
		SettingsPanel.add(self.APIKeyField, gbc)

		# Timeout
		gbc.gridx = 0
		gbc.gridy = 1
		gbc.fill = GridBagConstraints.NONE
		gbc.weightx = 0.0
		SettingsPanel.add(self.TimeoutLabel, gbc)

		gbc.gridx = 1
		gbc.gridy = 1
		gbc.fill = GridBagConstraints.HORIZONTAL
		gbc.weightx = 1.0
		SettingsPanel.add(self.TimeoutField, gbc)

		# Delay
		gbc.gridx = 0
		gbc.gridy = 2
		gbc.fill = GridBagConstraints.NONE
		gbc.weightx = 0.0
		SettingsPanel.add(self.DelayLabel, gbc)

		gbc.gridx = 1
		gbc.gridy = 2
		gbc.fill = GridBagConstraints.HORIZONTAL
		gbc.weightx = 1.0
		SettingsPanel.add(self.DelayField, gbc)

		# Save button
		gbc.gridx = 1
		gbc.gridy = 3
		gbc.fill = GridBagConstraints.NONE
		gbc.anchor = GridBagConstraints.EAST
		gbc.weightx = 0.0
		SettingsPanel.add(self.saveButton, gbc)

		descriptionLabel = JLabel("Getting Started:")
		descriptionLabel.setFont(Font(descriptionLabel.getFont().getName(), Font.BOLD, 18))
		descriptionLabel.setAlignmentX(JLabel.LEFT_ALIGNMENT)

		self.descriptionArea = JTextArea("""
This plugin integrates Burp Suite with your BLACKBIRD Web App Pentesting Suite.
It allows you to scan your targets for security vulnerabilities. Scan results are only available on your dashboard.
https://app.blackbirdsec.eu/signin

Usage Guide:

1. Get your API key from your profile, visit https://app.blackbirdsec.eu/profile.

2. Enter your API key above and click 'Save'.

3. Right-click on a request in Burp Suite.

4. Select 'Scan for {VULNERABILITY}' from the context menu.
		""")
		self.descriptionArea.setEditable(False)
		self.descriptionArea.setLineWrap(True)
		self.descriptionArea.setWrapStyleWord(True)
		self.descriptionArea.setOpaque(False)
		self.descriptionArea.setFont(Font(self.descriptionArea.getFont().getName(), Font.PLAIN, 16))
		self.descriptionArea.setAlignmentX(JTextArea.LEFT_ALIGNMENT)

		# Add components to main panel
		self.mainPanel.add(titleLabel)
		self.mainPanel.add(Box.createRigidArea(Dimension(0, 20)))
		self.mainPanel.add(settingsLabel)
		self.mainPanel.add(Box.createRigidArea(Dimension(0, 2)))
		self.mainPanel.add(SettingsPanel)
		self.mainPanel.add(Box.createRigidArea(Dimension(0, 20)))
		self.mainPanel.add(descriptionLabel)
		self.mainPanel.add(Box.createRigidArea(Dimension(0, 5)))
		self.mainPanel.add(self.descriptionArea)

		callbacks.addSuiteTab(self)

		# Load API key from extension settings
		self.APIKey = callbacks.loadExtensionSetting("APIKey")
		if self.APIKey:
			self.APIKeyField.setText(self.APIKey)
			self.APIKeyField.setForeground

		self.Timeout = callbacks.loadExtensionSetting("Timeout")
		if self.Timeout:
			self.TimeoutField.setText(self.Timeout)
			self.TimeoutField.setForeground
		else:
			self.TimeoutField.setText("7000")
			self.TimeoutField.setForeground

		self.Delay = callbacks.loadExtensionSetting("Delay")
		if self.Delay:
			self.DelayField.setText(self.Delay)
			self.DelayField.setForeground
		else:
			self.DelayField.setText("0")
			self.DelayField.setForeground

	def getTabCaption(self):
		return "BLACKBIRD Burpsuite Integration"

	def getUiComponent(self):
		return self.mainPanel

	def saveSettings(self, event):
		self.APIKey = self.APIKeyField.getText()
		self._callbacks.saveExtensionSetting("APIKey", self.APIKey)

		self.Timeout = self.TimeoutField.getText()
		self._callbacks.saveExtensionSetting("Timeout", self.Timeout)

		self.Delay = self.DelayField.getText()
		self._callbacks.saveExtensionSetting("Delay", self.Delay)

		self.stdout.println("Configuration settings saved successfully!")

	def createMenuItems(self, invocation):
		self.context = invocation
		menuList = ArrayList()
		menuList.add(JMenuItem("Scan URL for Command Injections", actionPerformed=lambda event: self.sendToAPI(event, "ciscanner")))
		menuList.add(JMenuItem("Scan URL for SQL Injections", actionPerformed=lambda event: self.sendToAPI(event, "sqls")))
		menuList.add(JMenuItem("Scan URL for SSRF", actionPerformed=lambda event: self.sendToAPI(event, "s9r")))
		menuList.add(JMenuItem("Scan URL for LFI", actionPerformed=lambda event: self.sendToAPI(event, "l8r")))
		menuList.add(JMenuItem("Scan URL for SSTI", actionPerformed=lambda event: self.sendToAPI(event, "inject49")))
		menuList.add(JMenuItem("Scan URL for XSS", actionPerformed=lambda event: self.sendToAPI(event, "xsscanner")))
		menuList.add(JMenuItem("Scan URL for Open URL Redirects", actionPerformed=lambda event: self.sendToAPI(event, "redirectx")))
		menuList.add(JMenuItem("Scan URL for CORS Misconfigurations", actionPerformed=lambda event: self.sendToAPI(event, "corscanner")))
		menuList.add(JMenuItem("Scan JavaScript file", actionPerformed=lambda event: self.sendToAPI(event, "jsauditor")))
		menuList.add(JMenuItem("Scan URL for all vulnerability types", actionPerformed=lambda event: self.sendToAPI(event, None)))

		return menuList

	def sendToAPI(self, event, scanner):
		if not self.APIKey:
			self.stderr.println("API key not set. Please set it in the extension tab.")
			return

		scanners = ["ciscanner", "sqls", "s9r", "l8r", "inject49", "xsscanner", "redirectx", "corscanner", "jsauditor"]

		if not any(s in str(scanner) for s in scanners) and scanner != None:
			self.stderr.println("Invalid scanner provided.")
			return

		http_traffic = self.context.getSelectedMessages()[0]
		request_info = self._helpers.analyzeRequest(http_traffic)
		request_body = self.getRequestBody(http_traffic)

		target = str(request_info.getUrl())

		self.stdout.println("[INFO:] API TOKEN LOADED: ****************************************************************")

		reqURI = "https://api.blackbirdsec.eu/api/" + str(scanner) + "/scan"

		if scanner == None:
			reqURI = "https://api.blackbirdsec.eu/api/scan"
		
		url = URL(reqURI)
		connection = url.openConnection()
		connection.setRequestMethod("PUT")
		connection.setDoOutput(True)
		connection.setRequestProperty("X-API-Key", self.APIKey)
		connection.setRequestProperty("Content-Type", "application/json")
		connection.setRequestProperty("User-Agent", "BLACKBIRD BurpSuite Integration (+https://blackbirdsec.eu/)")

		# Example payload
		config = {
			"targets": [
				target
			],
			"POSTBody": request_body,
			"payloadSet": 1,
			"browser": True,
			"headers": self.headersToString(request_info.getHeaders()),
			"delay": int(self.Delay),
			"timeout": int(self.Timeout)
		}

		if scanner == None:
			config = {
				"name": "",
				"targets": [ target ],
				"targetId": None,
				"type": "deep",
				"schedule": {
					"scheduled": False,
					"frequency": "once",
					"day": 1,
					"weekDay": 0,
					"month": 0,
					"hour": 0,
					"minute": 0
				},
				"config": {
					"options": {
						"SKIP_CONTENT_DISCOVERY": True,
						"SKIP_SSL": False,
						"MODE": "DEFAULT",
						"MAX_DEPTH": 3,
						"BROWSER": False,
						"EXTERNAL_SOURCES": False,
						"JAVASCRIPT_PARSING": False,
						"SUBMIT_FORMS": False,
						"BRUTEFORCING": False,
						"FILTER_TARGETS": False,
						"HTTP_PORTS": "",
						"EXCLUDED_PATHS": [ ]
					},
					"VPNId": None,
					"headers": "",
					"delay": 0,
					"timeout": 7000,
					"notify": True,
					"scanners": [
						"waypoints",
						"cnamex",
						"corscanner",
						"redirectx",
						"xsscanner",
						"sqls",
						"s9r",
						"l8r",
						"ciscanner",
						"inject49",
						"jsauditor"
					]
				}
			}

		payload = json.dumps(config)
		connection.getOutputStream().write(payload.encode('utf-8'))

		response_code = connection.getResponseCode()

		self.stdout.println("[INFO:] Request sent to API!")
		self.stdout.println("[DEBUG:] Response code: " + str(response_code))

		if response_code == 200:  # Assuming 200 is the success code
			reader = BufferedReader(InputStreamReader(connection.getInputStream()))
			response_body = ""
			line = reader.readLine()
			while line is not None:
				response_body += line
				line = reader.readLine()
			reader.close()

			try:
				response_json = json.loads(response_body)
				if response_json.get("success"):
					scan_id = response_json.get("id")
					self.stdout.println("[SUCCESS:] Scan initiated successfully. Scan ID: " + str(scan_id))
				else:
					self.stdout.println("[WARNING:] Request was successful, but 'success' property was false.")
			except json.JSONDecodeError:
				self.stderr.println("[ERROR:] Failed to parse JSON response.")
		else:
			self.stderr.println("[ERROR:] Request failed with response code: " + str(response_code))

		connection.disconnect()

	def getRequestBody(self, http_traffic):
		request = http_traffic.getRequest()
		request_str = self._helpers.bytesToString(request)

		# Split the request string to extract the body
		body_start = request_str.find("\r\n\r\n") + 4
		request_body = request_str[body_start:]

		if len(request_body) == 0:
			return None
		else:
			return request_body

	def headersToString(self, headers):
		block_list = ["Host", "DNT", "Cache-Control", "Upgrade-Insecure-Requests",
		"Accept", "Accept-Language", "Accept-Encoding", "Connection", "Content-Length",
		"Sec-Ch-Ua-Platform", "Sec-GPC", "Sec-Fetch-Mode", "Sec-Fetch-Dest", "Sec-Fetch-Site",
		"Sec-Ch-Ua-Mobile", "Sec-Ch-Ua", "Priority"]
		headers_str = ""
		# Skip the first line (HTTP method, path, and HTTP version)
		for header in headers[1:]:
			# Skip headers in the block list
			if any(block_header in header for block_header in block_list):
				continue
			headers_str += header + ";;"
		return headers_str

	class PlaceholderFocusListener(FocusListener):
		def __init__(self, textfield, placeholder):
			self.textfield = textfield
			self.placeholder = placeholder

		def focusGained(self, e):
			if self.textfield.getText() == self.placeholder:
				self.textfield.setText("")
				self.textfield.setForeground(Color.WHITE)  # Change to white when focused

		def focusLost(self, e):
			if self.textfield.getText() == "":
				self.textfield.setText(self.placeholder)
				self.textfield.setForeground(Color.LIGHT_GRAY)  # Change back to light gray for placeholder
