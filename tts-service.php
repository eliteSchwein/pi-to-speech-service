<?php
 header('Content-type: text/plain; charset=utf-8');
 #error_reporting(E_ALL);
 #ini_set('display_errors', 1);
	
	
 # CONFIGURATION
const COMMAND_USER = 'sudo -u pi python';
const COMMAND_FILE = '~/pi-to-speech-service/pi-to-speech-service.py ';
const COMMAND_EXEC = COMMAND_USER . ' ' . COMMAND_FILE;
	
 init();
 
 function init(){	
 	 $cmdParams = initParams();

 	 executeTTS($cmdParams);
 }
 
 function initParams(){
		$paramQuery = $_SERVER['QUERY_STRING'];  
		parse_str($paramQuery, $queryParams); #parses the query string into an array
		
		if($_SERVER['REQUEST_METHOD'] === 'POST') {
            $queryParams['text'] = @file_get_contents('php://input');
		}else{
            if(!isset($queryParams['text'])) {
                $queryParams['text'] =  urldecode($paramQuery);
  			}
		}

        $headers = getallheaders();
	
	    $cmdParams = "";
		foreach($queryParams as $key => $value) {
			$cmdParams .= (strlen($key)>2?' --' : ' -').$key;
			if($value != ''){
				$cmdParams .= '="'.$value.'"';
			}
		}

         if(array_key_exists('Tts-Language', $headers)) {
             $cmdParams .= ' --language="'.$headers['Tts-Language'].'"';
         }

     if(array_key_exists('Tts-provider', $headers)) {
         $cmdParams .= ' --provider="'.$headers['Tts-provider'].'"';
     }

 		return $cmdParams;
 }

 function executeTTS($cmdParams){	  
		$command = escapeshellcmd(COMMAND_EXEC . $cmdParams);
		echo "execute command: " . $command;
		
		$output = shell_exec($command);
		echo $output;	
 }