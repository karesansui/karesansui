// This file is part of Karesansui Core.
//
// Copyright (C) 2009-2012 HDE, Inc.
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.
//
// Authors:
//     Kei Funagayama <kei@karesansui-project.info>
//

var CHECK_EMPTY     = (1<<0); // whether textbox is empty or not
var CHECK_VALID     = (1<<1); // whether value is valid or not
var CHECK_NOTROOT   = (1<<2); // whether / (root) directory is specified or not
var CHECK_STARTROOT = (1<<3); // whether value begins with / (root)
var CHECK_MIN       = (1<<4); // Minimum value checker
var CHECK_MAX       = (1<<5); // Maximum value checker
var ALLOW_REGEX     = (1<<6); // Allow regular expression
var CHECK_LENGTH    = (1<<7); // whether the length of string is long enough
var CHECK_ONLYINT   = (1<<8); // whether value consists of the integer only
var CHECK_ONLYSPACE = (1<<9); // whether value consists of the space char only
var CHECK_CONSISTENCY = (1<<10);// check whether it is consistent with two data currently

var ERROR_MSG = "";

function minisprintf(format, val){
  if(typeof(val) == "string"){
    format = format.replace(/%s/,val);
  }else if(typeof(val) == "number"){
    format = format.replace(/%d/,val);
  }else{
    for(i = 1; i < val.length; i++){
      var reg = new RegExp('%[sd]|%' + i + '\\$[sd]');
      format = format.replace(reg,val[i]);
    }
  }
  return format;
}

function trim(value){
  var s;
  s = value;
  s = s.replace(/^[ \t\r\n]+/, "");
  s = s.replace(/[ \t\r\n]+$/, "");
  return s;
}

function netmask_to_netlen(netmask){
  var netlen = -1;
  var reg    = /^(\d+)\.(\d+)\.(\d+)\.(\d+)$/;
  var octet  = netmask.match(reg);

  if(octet) {
    var netmask_bit = parseInt(octet[1])*256*256*256
                    + parseInt(octet[2])*256*256
                    + parseInt(octet[3])*256
                    + parseInt(octet[4]);

    var base_bit    = 255*256*256*256
                    + 255*256*256
                    + 255*256
                    + 255;

    for(var cnt=0; cnt<32; cnt++) {
      if(!(netmask_bit ^ (base_bit<<cnt))) {
        netlen = 32 - cnt;
      }
    }
  }
  return netlen;
}

function check_empty( form, name ){

  if(form.jquery != undefined) {
    form = form[0];
  }

  var ret_val = true;
  if(!(form.value)){
    ERROR_MSG += minisprintf("${_('%s is missing.')}",name);
    ERROR_MSG += "\n";
    ret_val = false;
  }

  if(!ret_val){
    form.focus();
  }
  return ret_val;
}

function check_length(form, name, min, max){

  if(form.jquery != undefined) {
    form = form[0];
  }

  ret_val = true;
  if(typeof(min) != "undefined") {
    if(form.value.length < min){
      ERROR_MSG += minisprintf("${_('%1$s must be longer than %2$d characters.')}", Array(0,name,min));
      ERROR_MSG += "\n";
      ret_val = false;
    }
  }
  if(typeof(max) != "undefined") {
    if(max < form.value.length){
      ERROR_MSG += minisprintf("${_('%1$s must be shorter than %2$d characters.')}", Array(0,name,max));
      ERROR_MSG += "\n";
      ret_val = false;
    }
  }

  if(!ret_val){
    form.focus();
  }
  return ret_val;
}

function check_string(form, check, name, regex, min, max){

  if(form.jquery != undefined) {
    form = form[0];
  }

  ret_val = true;
  if(check & CHECK_EMPTY){
    ret_val = check_empty(form, name) && ret_val;
  }

  if(ret_val && check & CHECK_LENGTH){
    ret_val = check_length(form, name, min, max) && ret_val;
  }

  if((check & CHECK_VALID) && regex){
    if((str = form.value.match(regex))){
      var arr = new Array(2);
      arr[1] = name;
      arr[2] = str;
      ERROR_MSG += minisprintf("${_('%1$s includes invalid character[s] %2$s.')}",arr);
      ERROR_MSG += "\n";
      ret_val = false;
    }
  }

  if(check & CHECK_ONLYSPACE){
    var reg = /^\s+$/;
    if(form.value.match(reg)){
      ERROR_MSG += minisprintf("${_('%s must not consist of only blank characters.')}", name);
      ERROR_MSG += "\n";
      ret_val = false;
    }
  }

  if(!ret_val){
    form.focus();
  }
  return ret_val;
}

function check_number(form, check, name, min, max){

  if(form.jquery != undefined) {
    form = form[0];
  }

  ret_val = true;
  if(check & CHECK_EMPTY){
    ret_val = check_empty(form, name) && ret_val;
  }

  if(form.value && ret_val){
    if(check & CHECK_VALID){
      var reg = /^[-+]?[0-9]+$/;
      if(!form.value.match(reg)){
	ERROR_MSG += minisprintf("${_('%s is not numerical value.')}",name);
	ERROR_MSG += "\n";
	ret_val = false;
      }
    }
    if(ret_val && check & CHECK_MIN){
      if(parseInt(form.value) < min){
	var arr = new Array(2);
	arr[1] = name;
	arr[2] = String(min);
	ERROR_MSG += minisprintf("${_('%1$s must be greater than %2$s.')}",arr);
	ERROR_MSG += "\n";
	ret_val = false;
      }
    }
    if(ret_val && check & CHECK_MAX){
      if(parseInt(form.value) > max){
	var arr = new Array(2);
	arr[1] = name;
	arr[2] = String(max);
	ERROR_MSG += minisprintf("${_('%1$s must be smaller than %2$s.')}",arr);
	ERROR_MSG += "\n";
	ret_val = false;
      }
    }
  }
  if(!ret_val){
    form.focus();
  }
  return ret_val;
}

function check_unique_key(form, check, name){  
  if(form.jquery != undefined) {
    form = form[0];
  }

  var ret_val = true;
  if(check & CHECK_EMPTY){
    ret_val = check_empty(form, name) && ret_val;
  }

  if(form.value && ret_val){
    if(check & CHECK_VALID){
      var reg = /^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$/;
        if(!(form.value.match(reg))){
            ERROR_MSG += minisprintf("${_('%s is invalid format.')}",name);
            ERROR_MSG += "\n";
            ret_val = false;
        }
    }
  }
  if(!ret_val){
    form.focus();
  }
  return ret_val;
}

function check_directory( form, check, name ){

  if(form.jquery != undefined) {
    form = form[0];
  }

  var ret_val = true;
  if(check & CHECK_EMPTY){
    ret_val = check_empty(form, name) && ret_val;
  }

  if(form.value && ret_val){
    if(check & CHECK_STARTROOT){
      var reg = /^\/+/;
      if(!(form.value.match(reg))){
	ERROR_MSG += minisprintf("${_('%s must start with /.')}", name);
	ERROR_MSG += "\n";
	ret_val = false;
      }
    }

    if(check & CHECK_NOTROOT){
      var reg = /^\/+$/;
      if(form.value.match(reg)){
	ERROR_MSG += minisprintf("${_('%s must not be root directory.')}",name);
	ERROR_MSG += "\n";
	ret_val = false;
      }
    }

    if(check & CHECK_VALID){
      var reg = '+\._\(\)\'&@a-zA-Z0-9\/-';
	    
      if(check & ALLOW_REGEX){
	regex = '\\x5d*{}[?';
	regex_str = ']*{}[?';
      }else{
	regex = "";
	regex_str = "";
      }
      reg = regex + reg;
      reg = new RegExp("[^"+reg+"]");
      if((str = form.value.match(reg))){
	var arr = new Array(2);
	arr[1] = name;
	arr[2] = str;
	ERROR_MSG += minisprintf("${_('%1$s includes invalid character[s] %2$s.')}",arr);
	ERROR_MSG += "\n" + "${_('Available characters are')}" + "\n"
	  + minisprintf("${_('0-9 a-z A-Z @ & ( ) + - . _ %s')}",
			regex_str);
	ERROR_MSG += "\n";
	ret_val = false;
      } 
    }
  }

  if(!ret_val){
    form.focus();
  }
  return ret_val;
}

function check_filename(form, check, name){

  if(form.jquery != undefined) {
    form = form[0];
  }

  ret_val = true;
  if(check & CHECK_EMPTY){
    ret_val = check_empty(form, name) && ret_val;
  }

  if(form.value && ret_val){
    if(check & CHECK_VALID){
      var reg = '+\._\(\)\'&@a-zA-Z0-9\/-';
   
      if(check & ALLOW_REGEX){
	regex = '\\x5d*{}[?';
	regex_str = ']*{}[?';
      }else{
	regex = "";
	regex_str = "";
      }
      reg = regex + reg;
      reg = new RegExp("[^"+reg+"]");
      if((str = form.value.match(reg))){
	var arr = new Array(2);
	arr[1] = name;
	arr[2] = str;
	ERROR_MSG += minisprintf("${_('%1$s includes invalid character[s] %2$s.')}",arr);
	ERROR_MSG += "\n" + "${_('Available characters are')}" + "\n"
	  + minisprintf("${_('0-9 a-z A-Z @ & ( ) + - . _ %s')}",
			regex_str);
	ERROR_MSG += "\n";
	ret_val = false;
      } else {
        reg = /\.[\x5d\*\{\}\[\?]/;
        if((check & ALLOW_REGEX) && (str = form.value.match(reg))){
	  var arr = new Array(2);
	  arr[1] = name;
	  arr[2] = str;
	  ERROR_MSG += minisprintf("${_('%1$s includes invalid character[s] %2$s.')}",arr);
	  ERROR_MSG += "\n";
	  ret_val = false;
        }
      }
    }

    if(check & CHECK_STARTROOT){
      var reg = /^\/+/;
      if(!(form.value.match(reg))){
	ERROR_MSG += minisprintf("${_('%s must start /.')}", name);
	ERROR_MSG += "\n";
	ret_val = false;
      }
    }

    if(check & CHECK_NOTROOT){
      var reg = /^\/+$/;
      if(form.value.match(reg)){
	ERROR_MSG += minisprintf("${_('%s must not be root directory.')}",name);
	ERROR_MSG += "\n";
	ret_val = false;
      }
    }
  }

  if(!ret_val){
    form.focus();
  }
  return ret_val;
}

function check_username(form, check, name, min, max){

  if(form.jquery != undefined) {
    form = form[0];
  }

  ret_val = true;
  if(check & CHECK_EMPTY){
    ret_val = check_empty(form, name) && ret_val;
  }

  if(ret_val && check & CHECK_LENGTH){
    ret_val = check_length(form, name, min, max) && ret_val;
  }

  if(form.value && ret_val){
    if(check & CHECK_VALID){
      var reg = /^[a-z]/;
      if(!form.value.match(reg)){
	      ERROR_MSG += minisprintf("${_('%s must begin with alphabet.')}",name);
	      ERROR_MSG += "\n";
	      ret_val = false;
      }else{
	      reg = /^[a-z][-_.0-9a-z]*$/;
	      if(!form.value.match(reg)){
	          str =(form.value.match(/[^-_.0-9a-z]/));
	          var arr = new Array(2);
	          arr[1] = name;
	          arr[2] = str;
	          ERROR_MSG += minisprintf("${_('%1$s includes invalid character[s] %2$s.')}",arr);
	          ERROR_MSG += "\n" + "${_('Available characters are')}" + "\n"
	              + "${_('0-9 a-z - . _')}";
	          ERROR_MSG += "\n";
	          ret_val = false;
	      }
      }
    }
  }

  if(check & CHECK_ONLYSPACE){
    var reg = /^\s+$/;
    if(form.value.match(reg)){
      ERROR_MSG += minisprintf("${_('%s must not consist of only blank characters.')}", name);
      ERROR_MSG += "\n";
      ret_val = false;
    }
  }

  if(!ret_val){
    form.focus();
  }
  return ret_val;
}

function check_username_with_num(form, check, name, min, max){

  if(form.jquery != undefined) {
    form = form[0];
  }

  ret_val = true;
  if(check & CHECK_EMPTY){
    ret_val = check_empty(form, name) && ret_val;
  }

  if(ret_val && check & CHECK_LENGTH){
    ret_val = check_length(form, name, min, max) && ret_val;
  }

  if(form.value && ret_val){
    if(check & CHECK_VALID){
      var reg = /^[a-zA-Z0-9]/;
      if(!form.value.match(reg)){
	      ERROR_MSG += minisprintf("${_('%s must begin with alphabet or number.')}",name);
	      ERROR_MSG += "\n";
	      ret_val = false;
      }else{
	      reg = /^[a-zA-Z0-9][-_.0-9A-Za-z]*$/;
	      if(!form.value.match(reg)){
	          str =(form.value.match(/[^-_.0-9A-Za-z]/));
	          var arr = new Array(2);
	          arr[1] = name;
	          arr[2] = str;
	          ERROR_MSG += minisprintf("${_('%1$s includes invalid character[s] %2$s.')}",arr);
	          ERROR_MSG += "\n" + "${_('Available characters are')}" + "\n"
	              + "${_('0-9 a-z A-Z - . _')}";
	          ERROR_MSG += "\n";
	          ret_val = false;
	      }
      }
    }
  }

  if(!ret_val){
    form.focus();
  }
  return ret_val;
}

function check_network_name(form, check, name) {
  if(form.jquery != undefined) {
    form = form[0];
  }

  ret_val = true;
  if (check & CHECK_EMPTY) {
    ret_val = check_empty(form, name) && ret_val;
    return ret_val;
  }
  if (check & CHECK_VALID) {
    regex = /^[a-zA-Z0-9][a-zA-Z0-9 \.\:]{0,24}$/; // what is a valid network name for libvirt?
    if (!form.value.match(regex)) {
      ERROR_MSG += minisprintf("${_('%s includes invalid character[s].')}", name);
      ret_val = false;
    }
  }
  return ret_val;
}

function check_netdev_name(form, check, name) {
  if(form.jquery != undefined) {
    form = form[0];
  }

  ret_val = true;
  if (check & CHECK_EMPTY) {
    ret_val = check_empty(form, name) && ret_val;
    return ret_val;
  }
  if (check & CHECK_VALID) {
    regex = /^[a-z][a-z0-9\.\:]{1,12}$/; // what is a valid net dev name in linux?
    if (!form.value.match(regex)) {
      ERROR_MSG += minisprintf("${_('%s includes invalid character[s].')}", name);
      ret_val = false;
    }
  }
  return ret_val;
}
function check_domainname(form, check, name, domain, min, max){

  if(form.jquery != undefined) {
    form = form[0];
  }

  ret_val = true;
  if(!domain){
    domain = "your.domain.name";
  }
  if(check & CHECK_EMPTY){
    ret_val = check_empty(form, name) && ret_val;
  }

  if(ret_val && check & CHECK_LENGTH){
    ret_val = check_length(form, name, min, max) && ret_val;
  }

  if(form.value && ret_val){
    if(check & CHECK_VALID){
      var reg = /\./;
      if(!form.value.match(reg) && form.value != "localhost"){
	ERROR_MSG += minisprintf("${_('%s must include at least one dot . character.')}",name);
	ERROR_MSG += "\n";
	ret_val = false;
      }
      var reg1 = /^\./;
      var reg2 = /\.$/;
      var reg3 = /\.\./;
      var reg4 = /-\./;
      var reg5 = /\.-/;
      if(form.value.match(reg1) || form.value.match(reg2) || form.value.match(reg3)
	 || form.value.match(reg4) || form.value.match(reg5)){
	var arr = new Array(2);
	arr[1] = name;
	arr[2] = domain;
	ERROR_MSG += minisprintf("${_('%1$s must be specified like %2$s.')}",arr);
	ERROR_MSG += "\n";
	ret_val = false;
      }
	      
      reg = /[^-a-zA-Z0-9\.]/;
      if(ret_val && (str = form.value.match(reg))){
	var arr = new Array(2);
	arr[1] = name;
	arr[2] = str;
	ERROR_MSG += minisprintf("${_('%1$s includes invalid character[s] %2$s.')}",arr);
	ERROR_MSG += "\n" + "${_('Available characters are')}" + "\n"
	  + "${_('a-z A-Z 0-9 . -')}";
	ERROR_MSG += "\n";
	ret_val = false;
      }
    }
  }  
  if(!ret_val){
    form.focus();
  }
  return ret_val;
}

function check_hostname(form, check, name, min, max){

  if(form.jquery != undefined) {
    form = form[0];
  }

  ret_val = true;
  if(check & CHECK_EMPTY){
    ret_val = check_empty(form, name) && ret_val;
  }

  if(ret_val && check & CHECK_LENGTH){
    ret_val = check_length(form, name, min, max) && ret_val;
  }

  if(form.value && ret_val){
    if(check & CHECK_VALID){
      var reg = /\./;
      if(form.value.match(reg)){
	ERROR_MSG += minisprintf("${_('%s must not include dot . character.')}",name);
	ERROR_MSG += "\n";
	ret_val = false;
      }
      var reg1 = /-$/;
      var reg2 = /^-/;
      if(form.value.match(reg1) || form.value.match(reg2)){
	var arr = new Array(2);
	arr[1] = name;
	ERROR_MSG += minisprintf("${_('%s cannot begin or end with a hyphen.')}",name);
	ERROR_MSG += "\n";
	ret_val = false;
      }

      reg = /[^-a-zA-Z0-9]/;
      if(ret_val && (str = form.value.match(reg))){
	var arr = new Array(2);
	arr[1] = name;
	arr[2] = str;
	ERROR_MSG += minisprintf("${_('%1$s includes invalid character[s] %2$s.')}",arr);
	ERROR_MSG += "\n" + "${_('Available characters are')}" + "\n"
	  + "${_('a-z A-Z 0-9 . -')}";
	ERROR_MSG += "\n";
	ret_val = false;
      }
    }
  }  
  if(!ret_val){
    form.focus();
  }
  return ret_val;
}

function check_mailaddress(form, check, name, domain, min, max){

  if(form.jquery != undefined) {
    form = form[0];
  }

  ret_val = true;
  if(!domain){
    domain = "your.domain.name";
  }

  if(check & CHECK_EMPTY){
    ret_val = check_empty(form, name) && ret_val;
  }

  if(ret_val && check & CHECK_LENGTH){
    ret_val = check_length(form, name, min, max) && ret_val;
  }

  if(form.value && ret_val){
    if(check & CHECK_VALID){
      var treg = /^([^@]+)@(.+)?$/;
      if(form.value.match(treg)){
        var tstr1 = RegExp.$1;
        var tstr2 = RegExp.$2;
        var formval = form.value;
        form.value = tstr1;
        ret_val = ret_val && check_username_with_num(form, check, name);
        form.value = formval;
        formval = form.value;
        form.value = tstr2;
        ret_val = ret_val && check_domainname(form, CHECK_EMPTY | check, minisprintf("${_('Domain name part of %s')}",name),domain);
        form.value = formval;
      }else{
        ERROR_MSG += minisprintf("${_('%s is invalid format.')}",name);
        ERROR_MSG += "\n";
        ERROR_MSG += minisprintf("${_('Please specify like username@%s.')}",domain);
        ERROR_MSG += "\n";
        ret_val = false;
      }
    }
  }

  if(!ret_val){
    form.focus();
  }
  return ret_val;
}

function check_ipaddr(form, check, name) {

  if(form.jquery != undefined) {
    form = form[0];
  }

  ret_val = true;
  if(check & CHECK_EMPTY){
    ret_val = check_empty(form, name) && ret_val;
  }

  if(ret_val && check & CHECK_VALID){
    var reg = /^(\d+)\.(\d+)\.(\d+)\.(\d+)$/;
    var ar = form.value.match(reg);

    if(!ar) {
      ERROR_MSG += minisprintf("${_('%s is in invalid format')}" + "\n", name);
      ret_val = false;
    } else if(((parseInt(ar[1]) < 0) || (parseInt(ar[1]) > 255)) ||
	      ((parseInt(ar[2]) < 0) || (parseInt(ar[2]) > 255)) ||
	      ((parseInt(ar[3]) < 0) || (parseInt(ar[3]) > 255)) ||
	      ((parseInt(ar[4]) < 0) || (parseInt(ar[4]) > 255))) {
      ERROR_MSG += minisprintf("${_('%s is in invalid format.')}" + "\n", name);
      ret_val = false;
    }
  }

  if(!ret_val){
    form.focus();
  }
  return ret_val;

}

function check_networkaddr(form, check, name){

  if(form.jquery != undefined) {
    form = form[0];
  }

  ret_val = true;
  if(check & CHECK_EMPTY){
    ret_val = check_empty(form, name) && ret_val;
  }

  if(ret_val && check & CHECK_VALID){
    var reg3 = /^(\d+)\.(\d+)\.(\d+)$/;
    var reg2 = /^(\d+)\.(\d+)$/;
    var reg1 = /^(\d+)$/;
    if(form.value.match(reg3)){
      ar=form.value.match(reg3);
      if(((parseInt(ar[1]) < 0) || (parseInt(ar[1]) > 255)) ||
	 ((parseInt(ar[2]) < 0) || (parseInt(ar[2]) > 255)) ||
	 ((parseInt(ar[3]) < 0) || (parseInt(ar[3]) > 255))){
	ERROR_MSG += minisprintf("${_('%s is in invalid format.')}" + "\n", name);
	ret_val = false;
      }
    }else if(form.value.match(reg2)){
      ar=form.value.match(reg2);
      if(((parseInt(ar[1]) < 0) || (parseInt(ar[1]) > 255)) ||
         ((parseInt(ar[2]) < 0) || (parseInt(ar[2]) > 255))){
	ERROR_MSG += minisprintf("${_('%s is in invalid format.')}" + "\n", name);
	ret_val = false;
      }
    }else if(form.value.match(reg1)){
      ar=form.value.match(reg1);
      if(((parseInt(ar[1]) < 0) || (parseInt(ar[1]) > 255))){
	ERROR_MSG += minisprintf("${_('%s is in invalid format.')}" + "\n", name);
	ret_val = false;
      }
    }else{
      ERROR_MSG += minisprintf("${_('%s is in invalid format.')}" + "\n", name);
      ret_val = false;
    }
  }

  if(!ret_val){
    form.focus();
  }
  return ret_val;
}

function check_cidr(form, check, name){

  if(form.jquery != undefined) {
    form = form[0];
  }

  ret_val = true;
  if(check & CHECK_EMPTY){
    ret_val = check_empty(form, name) && ret_val;
  }

  if(ret_val && check & CHECK_VALID){

    var cidr_reg = /^(([0-9]{1,3}\.){3}([0-9]{1,3}))\/([0-9]{1,2})$/;
    var netmask_reg = /^(([0-9]{1,3}\.){3}([0-9]{1,3}))\/(([0-9]{1,3}\.){3}([0-9]{1,3}))$/;

    var ar = form.value.match(netmask_reg);
    var is_cidr = false;
    if(ar == null){
        is_cidr = true;
        ar = form.value.match(cidr_reg);
    } else {
        old_value = form.value;
        form.value = ar[4];
        ret_val = check_netmask(form, check, name);
        form.value = old_value;
    }

    if(ar){
      addr = ar[1];
      len = ar[4];
      old_value = form.value;
      form.value = addr;
      ret_val = check_ipaddr(form, check,
                     minisprintf("${_('Network address part of %s')}", name));
      form.value = old_value;
      if(ret_val){
        old_value = form.value;
        form.value = len;
        ret_val = check_number(form, 0, 32, check|CHECK_MIN|CHECK_MAX, 
                       minisprintf("${_('Network length part of %s')}", name));
        form.value = old_value;
      }

      if(ret_val && is_cidr == false && (check & CHECK_CONSISTENCY)){

        var reg = /^(\d+)\.(\d+)\.(\d+)\.(\d+)$/;
        var ar2 = addr.match(reg);
        var netlen = netmask_to_netlen(len);
        if(netlen < 32) {
          addr_bit  = parseInt(ar2[1])*256*256*256
                    + parseInt(ar2[2])*256*256
                    + parseInt(ar2[3])*256
                    + parseInt(ar2[4]) ;
          if(addr_bit << netlen) {
            ERROR_MSG += minisprintf("${_('Network and netmask is not match.[%s]')}" + "\n", name);
            ret_val = false;
          }
        }


      }
    } else {
      ERROR_MSG += minisprintf("${_('%s is in invalid format.')}" + "\n", name);
      ret_val = false;
    }
  }

  if(!ret_val){
    form.focus();
  }
  return ret_val;
}

function check_netmask(form, check, name) {

  if(form.jquery != undefined) {
    form = form[0];
  }

  ret_val = true;
  if(check & CHECK_EMPTY){
    ret_val = check_empty(form, name) && ret_val;
  }

  if(ret_val && check & CHECK_VALID){
    ret_val = check_ipaddr(form, check, name) && ret_val;

    if(ret_val && check) {

      var reg = /^(\d+)\.(\d+)\.(\d+)\.(\d+)$/;
      arr = form.value.match(reg);
      netmaskbit = parseInt(arr[1])*16777216
                 + parseInt(arr[2])*65536
                 + parseInt(arr[3])*256
                 + parseInt(arr[4]) ;
      basebit    = 255*16777216
                 + 255*65536
                 + 255*256
                 + 255 ;
      var flag = false;
      for(cnt=0; cnt<32; cnt++) {
        if(!(netmaskbit ^ (basebit<<cnt))) {
          flag = true;
        }
      }
      if(!flag) {
        ERROR_MSG += minisprintf("${_('%s is in invalid netmask format.')}" + "\n", name);
        ret_val = false;
      }
    }

  }

  if(!ret_val){
    form.focus();
  }
  return ret_val;

}

function check_macaddr(form, check, name) {
  
  if(form.jquery != undefined) {
    form = form[0];
  }

  ret_val = true;
  if(check & CHECK_EMPTY){
    ret_val = check_empty(form, name) && ret_val;
  }
  
  if(ret_val){
    if((check & CHECK_VALID) && (form.value.length > 0)){
      var reg = /^([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$/i;
      var ar = form.value.match(reg);
      if(!ar) {
        ERROR_MSG += minisprintf("${_('%s is in invalid format.')}" + "\n", name);
        ret_val = false;
      }
    }
  }

  if(!ret_val){
    form.focus();
  }
  return ret_val;
}

function check_password(pass1, pass2, check, name, min, max){

  if(pass1.jquery != undefined) {
    pass1 = pass1[0]
  }
  if(pass2.jquery != undefined) {
    pass2 = pass2[0]
  }

  ret_val = true;
  if(check & CHECK_EMPTY){
    if(pass1.value == "" || pass2.value == ""){
      ERROR_MSG += minisprintf("${_('%s is empty.')}" + "\n", name);
      ret_val = false;
    }
  }
  if((pass1.value || pass2.value) && ret_val){
    if(check & CHECK_VALID){
      if((pass1.value != "" || pass2.value != "" ) &&
	 pass1.value != pass2.value){
	ERROR_MSG += minisprintf("${_('%s is mismatch.')}" + "\n", name);
	ret_val = false;
      }
      if(ret_val && !is_ascii(pass1.value)){
    ERROR_MSG += minisprintf("${_('%s includes invalid character[s].')}" + "\n", name);
    ret_val = false;
      }
      if(ret_val && (check & CHECK_LENGTH)){

        if(typeof(min) != "undefined") {
	  if(pass1.value.length < min || pass2.value.length < min){
	    ERROR_MSG += minisprintf("${_('%1$s must be longer than %2$s.')}" + "\n", 
			     Array(0,name, min));
	    ret_val = false;
	  }
        }
        if(typeof(max) != "undefined") {
	  if(pass1.value.length > max || pass2.value.length > max){
	    ERROR_MSG += minisprintf("${_('%1$s must be shorter than %2$s.')}" + "\n", 
			     Array(0,name, max));
	    ret_val = false;
	  }
        }
      }
     if(check & CHECK_ONLYINT){
        if(pass1.value.match(/^[0-9]+$/)){
	  ERROR_MSG += minisprintf("${_('%s must not consist of only numbers.')}" + "\n", name);
	  ret_val = false;
	}
     }
    }
  }
  return ret_val;
}

function check_date(year,month,day,name){
  ret_val = true;
  if(!name){
    name = "";
  }
  if(isNaN(parseInt(year)) || year < 0){
    ERROR_MSG += minisprintf("${_('%1$s %2$s specification is invalid.')}",
			     Array(0,name, "${_('Year')}"));
    ERROR_MSG += "\n";
    ret_val = false;
  }

  if(year < 100){
    year += 2000;
  }
  if(ret_val && year < 1970){
    ERROR_MSG += minisprintf("${_('%1$s %2$s must be greater than 1970.')}",
			     Array(0,name, "${_('Year')}"));
    ERROR_MSG += "\n";
    ret_val = false;
  }
  if(ret_val && year > 2038){
    ERROR_MSG += minisprintf("${_('%1$s %2$s must be less than 2038.')}",
			     Array(0,name, "${_('Year')}"));
    ERROR_MSG += "\n";
    ret_val = false;
  }

  if(ret_val && (isNaN(parseInt(month)) || month < 1 || month > 12)){
    ERROR_MSG += minisprintf("${_('%1$s %2$s specification is invalid.')}",
			     Array(0,name, "${_('Month')}"));
    ERROR_MSG += "\n";
    ret_val = false;
  }

  if(ret_val){
    daymax = get_max_day(year,month);
    if(isNaN(parseInt(day)) || !daymax || day < 1 || day > daymax){
      ERROR_MSG += minisprintf("${_('%1$s %2$s specification is invalid.')}",
			       Array(0,name, "${_('Day')}"));
      ERROR_MSG += "\n";
      ret_val = false;
    }
  }
  return ret_val;
}

function get_max_day(year,month){
  if(isNaN(parseInt(year)) || year < 0){
    return false;
  }

  if(year < 100){
    year += 2000;
  }

  if(isNaN(parseInt(month)) || month < 1 || month > 12){
    return false;
  }

  switch(parseInt(month)){
  case 1:
  case 3:
  case 5:
  case 7:
  case 8:
  case 10:
  case 12:
    return 31;
    break;
  case 4:
  case 6:
  case 9:
  case 11:
    return 30;
    break;
  case 2:
    var daymax;
    if(!(year % 400)){
      daymax = 29;
    }else if(!(year % 100)){
      daymax = 28;
    }else if(!(year % 4)){
      daymax = 29;
    }else{
      daymax = 28;
    }
    return daymax;
    break;
  default:
    return '-';
    break;
  }
  return false;
}
		

function check_radio(radio, name) {
  ret_val = true;
  flag = false;

  if(radio.checked){
    flag = true;
  }

  for (i = 0; i < radio.length; i++) {
    if(radio[i].checked){
      flag = true;
    }
  }

  if(!flag){
    ERROR_MSG += minisprintf("${_('Please check %s.')}" + "\n", name);
    ret_val = false;
  }

  return ret_val;
}

function dir_analyze(){
  reg = /\/\//;
  while(this.value.match(reg)){
    this.value = this.value.replace(reg,'/');
  }
  reg = /^\/\.\/$/;
  while(this.value.match(reg)){
    this.value = this.value.replace(reg,'/');
  }
  reg = /^\/\.\.\/$/;
  while(this.value.match(reg)){
    this.value = this.value.replace(reg,'/');
  }
  reg = /^\.\/$/;
  while(this.value.match(reg)){
    this.value = this.value.replace(reg,'');
  }
  reg = /^\.\.\/$/;
  while(this.value.match(reg)){
    this.value = this.value.replace(reg,'');
  }
  reg = /\/[^\/]+\/\.\.\//;
  while(this.value.match(reg)){
    this.value = this.value.replace(reg,'/');
  }
  reg = /\/\.\//;
  while(this.value.match(reg)){
    this.value = this.value.replace(reg,'');
  }
  reg = /\/\/+$/;
  while(this.value.match(reg)){
    this.value = this.value.replace(reg,'/');
  }
}

function is_full_ipaddr(str){
  var reg = /^(\d+)\.(\d+)\.(\d+)\.(\d+)$/;
  var arr;
  var num;
  var addr;
  if((arr = str.match(reg))){
    for(num = 1; num <= 4; num++){
      addr = parseInt(arr[num]);
      if(addr < 0 || addr > 255){
	return false;
      }
    }
    return true;
  }
  return false;
}

function is_partial_ipaddr(str){
  var reg3 = /^(\d+)\.(\d+)\.(\d+)\.$/;
  var reg2 = /^(\d+)\.(\d+)\.$/;
  var reg1 = /^(\d+)\.$/;
  var arr;
  var num;
  var addr;
  
  if((arr = str.match(reg3))){
    for(num = 1; num <= 3; num++){
      addr = parseInt(arr[num]);
      if(addr < 0 || addr > 255){
	return false;
      }
    }
  }else if((arr = str.match(reg2))){
    for(num = 1; num <= 2; num++){
      addr = parseInt(arr[num]);
      if(addr < 0 || addr > 255){
	return false;
      }
    }
  }else if((arr = str.match(reg1))){
    addr = parseInt(arr[1]);
    if(addr < 0 || addr > 255){
      return false;
    }
  }else{
    return false;
  }
  return true;
}  

function is_ipaddr_range(str){
  var reg4 = /^(\d+)\.(\d+)\.(\d+)\.(\d+)-(\d+)$/;
  var reg3 = /^(\d+)\.(\d+)\.(\d+)-(\d+)\.$/;
  var reg2 = /^(\d+)\.(\d+)-(\d+)\.$/;
  var reg1 = /^(\d+)-(\d+)\.$/;
  var arr;
  var num;
  var addr;
  
  if((arr = str.match(reg4))){
    for(num = 1; num <= 5; num++){
      addr = parseInt(arr[num]);
      if(addr < 0 || addr > 255){
	return false;
      }
    }
    addr1 = parseInt(arr[4]);
    addr2 = parseInt(arr[5]);
    if(addr1 >= addr2){
	return false;
    }
  }else if((arr = str.match(reg3))){
    for(num = 1; num <= 4; num++){
      addr = parseInt(arr[num]);
      if(addr < 0 || addr > 255){
	return false;
      }
    }
    addr1 = parseInt(arr[3]);
    addr2 = parseInt(arr[4]);
    if(addr1 >= addr2){
	return false;
    }
  }else if((arr = str.match(reg2))){
    for(num = 1; num <= 3; num++){
      addr = parseInt(arr[num]);
      if(addr < 0 || addr > 255){
	return false;
      }
    }
    addr1 = parseInt(arr[2]);
    addr2 = parseInt(arr[3]);
    if(addr1 >= addr2){
	return false;
    }
  }else if((arr = str.match(reg1))){
    for(num = 1; num <= 2; num++){
      addr = parseInt(arr[num]);
      if(addr < 0 || addr > 255){
	return false;
      }
    }
    addr1 = parseInt(arr[1]);
    addr2 = parseInt(arr[2]);
    if(addr1 >= addr2){
	return false;
    }
  }else{
    return false;
  }
  return true;
}  

function is_network_netmask_pair(str){
  var reg = new RegExp("^([^/]+)\/([^/]+)$");
  var arr;
  var network;
  var netmask;
  if((arr = str.match(reg))){
    network = arr[1];
    netmask = arr[2];
    if(!is_full_ipaddr(network)){
      return false;
    }
    if(!is_full_ipaddr(netmask)){
      return false;
    }
    return true;
  }
  return false;
}

function is_CIDR(str){
  var reg = new RegExp("^([0-9\.]+)/([0-9]+)$");
  var arr;
  var network;
  var netmask;
  if((arr = str.match(reg))){
    network = arr[1];
    netmask = arr[2];
    if(!is_full_ipaddr(network)){
      return false;
    }
    if(netmask < 0 || netmask > 32){
      return false;
    }
    return true;
  }
  return false;
}

function is_domain(str){
  var reg = /^\.[-a-zA-Z0-9\.]*[-a-zA-Z0-9][^\.]*$/;
  if(str.match(reg)){
    return true;
  }
  return false;
}    

function is_FQDN(str){
  var reg = /^([a-zA-Z][-a-zA-Z0-9]*)(\..+)$/;
  var arr;
  if((arr = str.match(reg))){
    return is_domain(arr[2]);
  }
  return false;
}

function is_ascii(str){
  for (var cnt = 0; cnt < str.length; cnt++) {
    var _char = str.charCodeAt(cnt);
    if (_char < 0x20 || 0x7e < _char) {
      return false;
    }
  }
  return true;
}

function check_multi_mailaddress(form, check, name, domain){

  if(form.jquery != undefined) {
    form = form[0];
  }

  tmp_form = form.value;
  val = form.value.replace(/[ \t\r\n]+/,"");
  valarr = val.split(/,/);

  if (check & CHECK_EMPTY){
    empty_flag = true;
    for(i in valarr){
      if (!val){
        continue;
      }

      empty_flag = false;
      break;
    }

    if (empty_flag){
      ERROR_MSG += minisprintf("${_('%s is empty.')}", name);
      return false;
    }
  }

  if (check & CHECK_VALID){
    for(i in valarr){
      form.value = valarr[i];

      if (check_mailaddress(form, CHECK_VALID, name+" : "+form.value, domain)){
        continue;
      }

      form.value = tmp_form;
      return false;
    }
  }

  form.value = tmp_form;
  return true;
}

function check_decimal(form, min, max, check, name){

  if(form.jquery != undefined) {
    form = form[0];
  }

  var tmp_form, value, arr;

  value = tmp_form = form.value;
  value = value.replace(/^[ \t\r\n]+/, "");
  value = value.replace(/[ \t\r\n]+$/, "");

  if (value == ""){
    if (!(check & CHECK_EMPTY)){
      return true;
    }

    ERROR_MSG += minisprintf("${_('%s is empty.')}", name);
    ERROR_MSG += "\n";
    form.value = tmp_form;
    return false;
  }

  if ((check & CHECK_VALID) &&
      !value.match(/^[-+]?([0-9]+|[0-9]*\.[0-9]+)([Ee][-+]?[0-9]+)?$/)){
      ERROR_MSG += minisprintf("${_('%s is not a decimal value (should be a decimal value).')}"+"\n", name);
    ERROR_MSG += "\n";
    form.value = tmp_form;
    return false;
  }

  if ((check & CHECK_MIN) && (value < min)){
    arr = new Array();
    arr[1] = name;
    arr[2] = String(min);
    ERROR_MSG += minisprintf("${_('%1$s must be greater than %2$s.')}",arr);
    ERROR_MSG += "\n";
    form.value = tmp_form;
    return false;
  }

  if ((check & CHECK_MAX) && (value > max)){
    arr = new Array();
    arr[1] = name;
    arr[2] = String(max);
    ERROR_MSG += minisprintf("${_('%1$s must be smaller than %2$s.')}",arr);
    ERROR_MSG += "\n";
    form.value = tmp_form;
    return false;
  }

  form.value = tmp_form;
  return true;
}


function check_limit(form, limit, name){

  if(form.jquery != undefined) {
    form = form[0];
  }

  ret_val = true;
  if(form.value && ret_val){
    if(form.value > limit){
      var arr = new Array(2);
      arr[1] = name;
      arr[2] = String(limit);
      ERROR_MSG += minisprintf("${_('%1$s is limited to %2$s or less.')}",arr);
      ERROR_MSG += "\n";
      ret_val = false;
    }
  }
  if(!ret_val){
    form.focus();
  }

  return ret_val;
}

function check_datetime_string(form, check, name){
    if(form.jquery != undefined){
        form = form[0];
    }

    var ret_val = true;
    if(check & CHECK_EMPTY){
        ret_val = check_empty(form, name) && ret_val;
    }

    if(ret_val){
        if((check & CHECK_VALID) && (form.value.length != 0)){
            var format = "${USER_DATE_FORMAT[0]}";
            var year = 0;
            var month = 0;
            var day = 0;

            format_elems = format.split('/');
            form_elems = form.value.split('/');

            if(format_elems.length == form_elems.length){
                for(idx in format_elems){
                    if(format_elems[idx].indexOf("Y") != -1){
                        year = Number(form_elems[idx]);
                    }else if(format_elems[idx].indexOf("m") != -1){
                        month = Number(form_elems[idx]);
                    }else if(format_elems[idx].indexOf("d") != -1){
                        day = Number(form_elems[idx]);
                    }
                }
                ret_val = check_date(year,month,day,name) && ret_val;
            }else{
                ERROR_MSG += minisprintf("${_('%s is in invalid format.')}" + "\n", name);
                ret_val = false;
            }
        }
    }

    return ret_val;
}

function check_startfile(form, check, name){
    if(form.jquery != undefined){
        form = form[0];
    }

    var ret_val = true;
    if(check & CHECK_EMPTY){
        ret_val = check_empty(form, name) && ret_val;
    }

    if(form.value && ret_val){
        if(check & CHECK_VALID){
            var valid_check = false;
            // URI check
            var uri_reg = new RegExp(/(http|ftp):\/\/[\w.]+\/(\S*)/);
            var uri_check = false;
            if(form.value.match(uri_reg)){
                uri_check = true;
            }
            // file check
            var file_reg = new RegExp(/^\/+/);
            var file_check = false;
            if(form.value.match(file_reg)){
                file_check = true;
            }

            valid_check = (uri_check || file_check);
            if(!valid_check){
                ERROR_MSG += minisprintf("${_('%s is in invalid format.')}", name);
                ERROR_MSG += "\n";
                ret_val = false;
            }
        }
    }
    
    if(!ret_val){
        form.focus();
    }

    return ret_val;
}

function check_fraction(form, check, name, min, max, precision){
    if(form.jquery != undefined){
        form = form[0];
    }

    var ret_val = true;
    if(check & CHECK_EMPTY){
        ret_val = check_empty(form, name) && ret_val;
    }

    if(form.value && ret_val){
        var reg_dp = /^([-+]?[0-9]+)\.([0-9]+)$/;
        arr_dp = form.value.match(reg_dp);

        if(arr_dp) {
          integer  = arr_dp[1];
          fraction = arr_dp[2];
        } else {
          integer = form.value;
          fraction = "0";
        }

        if(check & CHECK_VALID){
            var reg1 = /^[-+]?[0-9]+$/;
            var reg2 = /^[0-9]+$/;

            if(!integer.match(reg1) || !fraction.match(reg2)){
                ERROR_MSG += minisprintf("${_('%s is not integer or decimal fraction.')}",name);
                ERROR_MSG += "\n\n";
                ret_val = false;
            }
            if(fraction.length > precision) {
                var arr = new Array(2);
                arr[1] = name;
                arr[2] = String(precision);
                ERROR_MSG += minisprintf("${_('(%1$s) Length of figures after point must be equal or less than %2$s.')}",arr);
                ERROR_MSG += "\n\n";
                ret_val = false;
            }
        }

        if(ret_val && check & CHECK_MIN){
            if(parseFloat(form.value) < min){
                var arr = new Array(2);
                arr[1] = name;
                arr[2] = String(min);
                ERROR_MSG += minisprintf("${_('%1$s must be greater than %2$s.')}",arr);
                ERROR_MSG += "\n\n";
                ret_val = false;
            }
        }

        if(ret_val && check & CHECK_MAX){
            if(parseFloat(form.value) > max){
                var arr = new Array(2);
                arr[1] = name;
                arr[2] = String(max);
                ERROR_MSG += minisprintf("${_('%1$s must be smaller than %2$s.')}",arr);
                ERROR_MSG += "\n\n";
                ret_val = false;
            }
        }
    }

    if(!ret_val){
        form.focus();
    }

    return ret_val;
}

function check_time_string(form, check, name){
    if(form.jquery != undefined){
        form = form[0];
    }

    var ret_val = true;
    if(check & CHECK_EMPTY){
        ret_val = check_empty(form, name) && ret_val;
    }

    if(ret_val){
        if((check & CHECK_VALID) && (form.value.length != 0)){
            var reg = /^([0-1][0-9]|[2][0-3]|[0-9]):[0-5][0-9]$/;
            if(!form.value.match(reg)){
                ERROR_MSG += minisprintf("${_('%s is in invalid format.')}",name);
                ERROR_MSG += "\n\n";
                ret_val = false;
            }
        }
    }

    return ret_val;
}
