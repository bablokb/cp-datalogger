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
    document.getElementById("configForm").submit();
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
              $("[name=STROBE_MODE]").val(["strobe"]);
            } else {
              $("[name=STROBE_MODE]").val(["cont"]);
            }
          } else if (name == "SIMPLE_UI") {
            if (value) {
              $("[name=SIMPLE_UI]").val(["simple_ui"]);
            } else {
              $("[name=SIMPLE_UI]").val(["tab_ui"]);
            }
          } else if (name == "TIME_TABLE") {
            update_time_table(value);
          } else if (['SENSORS','TASKS'].includes(name)) {
            $("[name="+name+"]").val(value.join(" "));
            $.each(value,function(_,v) {
                $("#"+name+"_"+v).toggleClass('ul_sel_li_active');
              });
          } else if (['HAVE_SD','HAVE_LORA'].includes(name)) {
            $("[name="+name+"]").prop("checked",value);
          } else {
            $("[name="+name+"]").val(value);
          }
        });
    });
}

function get_csv_list() {
  $.getJSON('/get_csv_list',
    function(csv_list) {
      $.each(csv_list.files,function(index,file) {
          var item = $("#file_0").
            clone(true).
            attr({"id": "file_"+(index+1),"href": file}).
            html(file);
          item.appendTo("#csv_list");
        });
      $("#file_0").remove();   // remove template
    });
}
