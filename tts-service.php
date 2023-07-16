<?php
 header('Content-type: text/plain; charset=utf-8');
 #error_reporting(E_ALL);
 #ini_set('display_errors', 1);
	
	
 # CONFIGURATION
 define("COMMAND_USER", 'sudo -u tts');
 define("COMMAND_FILE", '/opt/tts/pi-to-speech-service.py');
 define("COMMAND_EXEC", COMMAND_USER . ' ' . COMMAND_FILE);
	
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
             $cmdParams['language'] = $headers['Tts-Language'];
         }

 		return $cmdParams;
 }

 function executeTTS($cmdParams){	  
		$command = escapeshellcmd(COMMAND_EXEC . $cmdParams);
		#echo "execute command: " . $command;
		
		$output = shell_exec($command);
		echo $output;	
 }
?>