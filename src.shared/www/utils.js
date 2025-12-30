//-----------------------------------------------------------------------------
// Admin web-pages for the datalogger: utilities.
//
// Author: Bernhard Bablok
//
// Website: https://github.com/pcb-pico-datalogger
//-----------------------------------------------------------------------------

var currentTab = 0; // Current tab is set to be the first tab (0)

function showTab(n) {
  // This function will display the specified tab of the form...
  var x = document.getElementsByClassName("tab");
  x[n].style.display = "block";
  //... and fix the Previous/Next buttons:
  if (n == 0) {
    document.getElementById("prevBtn").style.display = "none";
  } else {
    document.getElementById("prevBtn").style.display = "inline";
  }
  if (n == (x.length - 1)) {
    document.getElementById("nextBtn").innerHTML = "Submit";
  } else {
    document.getElementById("nextBtn").innerHTML = "Next";
  }
  //... and run a function that will display the correct step indicator:
  fixStepIndicator(n)
}

function nextPrev(n) {
  // This function will figure out which tab to display
  var x = document.getElementsByClassName("tab");
  // Exit the function if any field in the current tab is invalid:
  if (n == 1 && !validateForm()) return false;
  // Hide the current tab:
  x[currentTab].style.display = "none";
  // if you have reached the end of the form...
  if (n == 1 && currentTab == x.length-1) {
    // ... the form gets submitted:
    $.ajax({
      url: '/save_config',
      type: 'post',
      dataType: 'text',
      data: $('#configForm').serialize()
      })
      .done(function(msg) {
        show_msg(msg,2000,goto_main_menu);
      })
      .fail(function( xhr, status, errorThrown ) {
          show_msg(`Error: ${errorThrown} (status: ${status})`);
    });
  } else {
    // Increase or decrease the current tab by 1:
    currentTab = currentTab + n;
  }
  // Otherwise, display the correct tab:
  showTab(currentTab);
}

function validateForm() {
  // This function deals with validation of the form fields
  var x, y, i, valid = true;
  x = document.getElementsByClassName("tab");
  y = x[currentTab].getElementsByClassName("mandatory");
  // A loop that checks every input field in the current tab:
  for (i = 0; i < y.length; i++) {
    // If a field is empty...
    if (y[i].value == "") {
      // add an "invalid" class to the field:
      y[i].classList.add("invalid");
      // and set the current valid status to false
      valid = false;
    } else {
      y[i].classList.remove("invalid");
    }
  }
  // If the valid status is true, mark the step as finished and valid:
  if (valid) {
    document.getElementsByClassName("step")[currentTab].className += " finish";
  }
  return valid; // return the valid status
}

function fixStepIndicator(n) {
  // This function removes the "active" class of all steps...
  var i, x = document.getElementsByClassName("step");
  for (i = 0; i < x.length; i++) {
    x[i].className = x[i].className.replace(" active", "");
  }
  //... and adds the "active" class on the current step:
  x[n].className += " active";
}

function create_select_options(name,options) {
  ul = $("#UL_"+name);
  li_templ = $("#"+name+"_T");
  $.each(options,function(index,opt) {
      item = li_templ.clone(true).
        attr({
            "onclick": `toggle_select_option($(this),"${name}","${opt}")`,
              "id": name+"_"+opt}).text(opt);
      item.appendTo(ul);
    });
  li_templ.remove();
}

function toggle_tt_mandatory(day) {
  $("[name=hs_"+day+"]").toggleClass('mandatory').removeClass('invalid');
  $("[name=he_"+day+"]").toggleClass('mandatory').removeClass('invalid');
  $("[name=hi_"+day+"]").toggleClass('mandatory').removeClass('invalid');
  $("[name=ms_"+day+"]").toggleClass('mandatory').removeClass('invalid');
  $("[name=me_"+day+"]").toggleClass('mandatory').removeClass('invalid');
  $("[name=mi_"+day+"]").toggleClass('mandatory').removeClass('invalid');
}

function update_time_table(table) {
  $.each(table,function(day,value) {
      h = value[0];
      m = value[1];
      if (h === null) {
        return;
      }
      $("[name=d_"+day+"]").prop("checked",true);
      $("[name=hs_"+day+"]").val(h[0]).addClass('mandatory');
      $("[name=he_"+day+"]").val(h[1]).addClass('mandatory');
      $("[name=hi_"+day+"]").val(h[2]).addClass('mandatory');
      $("[name=ms_"+day+"]").val(m[0]).addClass('mandatory');
      $("[name=me_"+day+"]").val(m[1]).addClass('mandatory');
      $("[name=mi_"+day+"]").val(m[2]).addClass('mandatory');
    });
}

function toggle_select_option(item,name,option) {
  var was_active = item.hasClass('ul_sel_li_active');
  item.toggleClass('ul_sel_li_active');
  input = $("#"+name);
  if (was_active) {
    // remove option from input-field
    re = new RegExp(`${option} | ${option} *$`,"g");
    input.val(input.val().replace(re,""));
  } else {
    // add at current caret position
    pos = input[0].selectionStart;
    if (pos == undefined) {
      pos = input.val().length;
    }
    content = input.val();
    input.val(`${content.slice(0,pos)} ${option} ${content.slice(pos)}`);
  }
}

function get_model() {
  $.getJSON('/get_model',
    function(model) {
      // set dynamic select options
      create_select_options("SENSORS",model._s_options);
      create_select_options("TASKS",model._t_options);

      // set defaults for strobe-mode and simple-ui
      $("[name=STROBE_MODE]").val(["strobe"]);
      $("[name=SIMPLE_UI]").val(["simple_ui"]);

      // update fields from model
      $.each(model,function(name,value) {
          if (name == "STROBE_MODE") {
            if (value) {
              $("[name=STROBE_MODE]").val(["True"]);
            } else {
              $("[name=STROBE_MODE]").val(["False"]);
            }
          } else if (name == "SIMPLE_UI") {
            if (value) {
              $("[name=SIMPLE_UI]").val(["True"]);
            } else {
              $("[name=SIMPLE_UI]").val(["False"]);
            }
          } else if (name == "TIME_TABLE") {
            update_time_table(value);
          } else if (['SENSORS','TASKS'].includes(name)) {
            $("[name="+name+"]").val(value.join(" "));
            $.each(value,function(_,v) {
                $("#"+name+"_"+v).toggleClass('ul_sel_li_active');
              });
          } else if (['HAVE_SD','HAVE_LIPO','HAVE_LORA'].includes(name)) {
            $("[name="+name+"]").prop("checked",value);
          } else {
            $("[name="+name+"]").val(value);
          }
        });
    });
}

function download_file(index,file) {
  window.open(file);
  btn_id = "#file_"+(index+1);
  $(btn_id).removeClass('menu-button');
}

function delete_file(ftype,index,file) {
  row_id = "#row_"+(index+1);
  $.ajax({
    url: file+'.delete',
    type: 'get',
    dataType: 'text',
        data: {}
    })
    .done(function(msg) {
      show_msg(`${file} deleted`);
      get_file_list(ftype);
    })
    .fail(function( xhr, status, errorThrown ) {
        show_msg(`Error: ${errorThrown} (status: ${status})`);
  });
}

function get_file_list(ftype) {
  $.getJSON(`/get_${ftype}_list`,
    function(file_list) {
      // clear existing list (keep template)
      $(`#${ftype}_list`).children().slice(1).remove();
      // rebuild list
      $.each(file_list.files,function(index,file) {
          var item = $("#row_0").clone(true).
            attr({"id": "row_"+(index+1)}).css('display','inline-flex');
          item.children().eq(0).
            attr({"id": "file_"+(index+1),
                  "onclick": `download_file(${index},'${file}')`}).
            html("&#128229; "+file);
          item.children().eq(1).
            attr({"id": "del_"+(index+1),
                  "onclick": `delete_file('${ftype}',${index},'${file}')`});
          item.appendTo(`#${ftype}_list`);
        });
    });
}

async function upload_config() {
  const file = $("#filename")[0];
  let response = await fetch('/upload_config',
                             {method: 'POST',
                                 body: file.files[0]
                                 });
  let msg = await response.text();
  show_msg(msg,5000);
};

function set_upload_btn() {
  $('#upload').prop('disabled',$('#filename').val().length==0);
}

function show_msg(text,time,callback) {
  $("#msgarea").text(text).show();
  setTimeout(function() {
      $("#msgarea").empty().hide();
      if (callback !== undefined) {
        callback();
      }
    }, time);
}

function update_status_fields(info) {
  d = new Date(info.dev_time*1000);
  $('#cp_version').text(info.cp_version);
  $('#board_id').text(info.board_id);
  $('#pcb_version').text(info.pcb_version);
  $('#dl_commit').text(info.dl_commit);
  $('#dev_time').text(d.toLocaleString(navigator.language,
                                       {"timeZone": "UTC"})
                      );
  $('#battery').text(info.battery);
  if (info.lipo && info.battery < 3.2 ||
      !info.lipo && info.battery < 2.2) {
    $('#upload').hide();
    $('#manual').hide();
    show_msg("battery low, please replace before proceeding!",10000);
  }
}

function get_status_info() {
  $.getJSON('/get_status_info',update_status_fields);
}

function goto_main_menu() {
  window.location.replace("index.html");
}

function set_time() {
  // get epoch time. getTimezoneOffset() is in minutes.
  d = new Date();
  ts = Math.floor((d.getTime()-d.getTimezoneOffset()*60000)/1000);
  $.post('/set_time',{ts},
         function(info) {
           update_status_fields(info);
           show_msg("time updated",5000);
         },'json');
}
