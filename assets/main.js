(function() {
  var NotificationStage, error, _ref, _ref1,
    __hasProp = {}.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

  window.Stage = (function() {
    function Stage() {
      this.time = 0;
      true;
    }

    Stage.prototype.bump = function() {
      return true;
    };

    Stage.prototype.trade_complete = function() {
      return true;
    };

    Stage.prototype.price_updated = function() {
      return true;
    };

    Stage.prototype.timer_begin = function() {
      return true;
    };

    Stage.prototype.end = function() {
      return true;
    };

    Stage.prototype.new_bid = function() {
      return true;
    };

    Stage.prototype.products_updated = function() {
      return true;
    };

    Stage.prototype.update = function() {
      return true;
    };

    return Stage;

  })();

  NotificationStage = (function(_super) {
    __extends(NotificationStage, _super);

    function NotificationStage() {
      _ref = NotificationStage.__super__.constructor.apply(this, arguments);
      return _ref;
    }

    NotificationStage.prototype.end = function() {
      return message.hide.call(message);
    };

    return NotificationStage;

  })(Stage);

  this.PyAPI = (function() {
    function PyAPI(socket) {
      var me;
      this.socket = socket != null ? socket : null;
      if (this.socket == null) {
        this.socket = window.socket;
      }
      this.response_handlers = [];
      this.event_responders = [];
      me = this;
      this.socket.onmessage = function(message) {
        return me.onmessage.call(me, message);
      };
      this.transaction('server_info', {}, function(data) {
        console.log("Attempted version validation. Received response:");
        console.log(data);
        if (data.version !== window.config.server_version) {
          throw "VERSION_ERROR: Invalid reported server version " + data.version + ". Expecting " + window.config.server_version;
        }
      });
    }

    PyAPI.prototype.onmessage = function(message) {
      message = JSON.parse(message.data);
      if (message.method == null) {
        throw "Received illegal message '" + (JSON.stringify(message)) + "' without method header.";
      } else if (message.method === "handle_callback") {
        if (this.response_handlers[message.args.callback_id] == null) {
          throw "Received illegal callback ID in a handle_callback response.";
        }
        console.log('Received callback with arguments: ', message.args);
        return this.response_handlers[message.args.callback_id].call(this, message.args.callback_args);
      } else {
        console.log('Received method call: ', message.method);
        console.log('Method call data: ', message.args);
        return this.trigger_event(message.method, message.args);
      }
    };

    PyAPI.prototype.generate_transaction_id = function(message) {
      return "T" + Math.random();
    };

    PyAPI.prototype.register_for_event = function(eventName, response) {
      if (this.event_responders[eventName] == null) {
        this.event_responders[eventName] = [];
      }
      return this.event_responders[eventName].push(response);
    };

    PyAPI.prototype.trigger_event = function(eventName, data) {
      var e, response, _i, _len, _ref1, _results;
      if (this.event_responders[eventName] != null) {
        _ref1 = this.event_responders[eventName];
        _results = [];
        for (_i = 0, _len = _ref1.length; _i < _len; _i++) {
          e = _ref1[_i];
          if (data.callback_id != null) {
            _results.push(response = e.call(window, data, new PyAPIResponder(data.callback_id, this)));
          } else {
            _results.push(e.call(window, data, new PyAPIDummyResponder()));
          }
        }
        return _results;
      }
    };

    PyAPI.prototype.transaction = function(method_name, args, responder) {
      var transaction_id, transmission;
      if (responder == null) {
        responder = null;
      }
      transmission = {
        method: method_name,
        args: args
      };
      if (responder != null) {
        transaction_id = this.generate_transaction_id(message);
        transmission.args.callback_id = transaction_id;
        this.response_handlers[transaction_id] = function(response) {
          return responder.call(this, response);
        };
      }
      this.socket.send(JSON.stringify(transmission));
      return console.log('Transaction sent: ', JSON.stringify(transmission));
    };

    PyAPI.prototype.reconnectWithSocket = function(new_socket) {
      this.socket.close();
      return this.socket = new_socket;
    };

    return PyAPI;

  })();

  this.PyAPIResponder = (function() {
    function PyAPIResponder(callback_id, parent) {
      this.callback_id = callback_id;
      this.parent = parent;
      true;
    }

    PyAPIResponder.prototype.respond = function(response) {
      this.parent.transaction('handle_callback', {
        callback_id: this.callback_id,
        callback_args: response
      });
      return true;
    };

    return PyAPIResponder;

  })();

  this.PyAPIDummyResponder = (function(_super) {
    __extends(PyAPIDummyResponder, _super);

    function PyAPIDummyResponder() {
      _ref1 = PyAPIDummyResponder.__super__.constructor.apply(this, arguments);
      return _ref1;
    }

    PyAPIDummyResponder.prototype.respond = function() {
      return true;
    };

    return PyAPIDummyResponder;

  })(PyAPIResponder);

<<<<<<< HEAD
=======
  window.Stage = (function() {
    function Stage() {
      this.time = 0;
      true;
    }

    Stage.prototype.bump = function() {
      return true;
    };

    Stage.prototype.trade_complete = function() {
      return true;
    };

    Stage.prototype.price_updated = function() {
      return true;
    };

    Stage.prototype.timer_begin = function() {
      return true;
    };

    Stage.prototype.end = function() {
      return true;
    };

    Stage.prototype.new_bid = function() {
      return true;
    };

    Stage.prototype.products_updated = function() {
      return true;
    };

    Stage.prototype.update = function() {
      return true;
    };

    return Stage;

  })();

  NotificationStage = (function(_super) {
    __extends(NotificationStage, _super);

    function NotificationStage() {
      return NotificationStage.__super__.constructor.apply(this, arguments);
    }

    NotificationStage.prototype.end = function() {
      return message.hide.call(message);
    };

    return NotificationStage;

  })(Stage);

  window.DayStage = (function(_super) {
    __extends(DayStage, _super);

    function DayStage() {
      true;
    }

    return DayStage;

  })(Stage);

>>>>>>> development
  window.jevents = [];

  window.jevent = function(eventName, eventAction) {
    var f, _i, _len, _ref2, _results;
    if (eventAction == null) {
      eventAction = null;
    }
    if (eventAction === null) {
      if (window.jevents[eventName] != null) {
        _ref2 = window.jevents[eventName];
        _results = [];
        for (_i = 0, _len = _ref2.length; _i < _len; _i++) {
          f = _ref2[_i];
          _results.push(f.call);
        }
        return _results;
      }
    } else {
      if (window.jevents[eventName] != null) {
        return window.jevents[eventName].push(eventAction);
      } else {
        return window.jevents[eventName] = [eventAction];
      }
    }
  };

  $(function() {
    var moving_average_samples;
    window.acc = {
      x: 0,
      y: 0,
      z: 0
    };
    window.avg_acc = false;
    moving_average_samples = 50;
    window.censor_gyroscope = false;
    return window.ondevicemotion = function(e) {
      var change, x, y, z;
      x = e.accelerationIncludingGravity.x;
      y = e.accelerationIncludingGravity.y;
      z = e.accelerationIncludingGravity.z;
      change = Math.abs(acc.x - x) + Math.abs(acc.y - y) + Math.abs(acc.z - z);
      window.acc = {
        x: x,
        y: y,
        z: z
      };
      if (change > 20 && !window.censor_gyroscope) {
        window.censor_gyroscope = true;
        window.stage.bump.call(window.stage);
        return setTimeout(function() {
          return window.censor_gyroscope = false;
        }, 500);
      }
    };
  });

  window.handleResize = function() {
    $('.statusbar').css('font-size', (0.9 * $('.statusbar').height()) + 'px');
    return $(window).scrollTop(0);
  };

  $(window).bind('resize', window.handleResize);

  $(function() {
    window.handleResize();
    $('.interface > div').each(function() {
      return $(this).hide();
    });
    if (($.ui == null) || ($.mobile == null)) {
      return location.reload(true);
    }
  });

  window.updateStatusBar = function() {
    return window.updateInterface();
  };

  window.updateInterface = function() {
    if (this.stage != null) {
      return this.stage.update();
    }
  };

  window.updateCountdown = function() {
    return $('.countdown').html(stage.time);
  };

  this.InventoryPanel = (function() {
    function InventoryPanel() {
      var _this = this;
      this.dom_element = $('.inventory');
      this.button_element = $('.inventory-button');
      this.button_element.click(function() {
        return _this.dom_element.toggle();
      });
      this.needsRefresh();
    }

    InventoryPanel.prototype.needsRefresh = function() {
      var n, p, _ref2;
      if (window.player != null) {
        _ref2 = window.player.products;
        for (n in _ref2) {
          p = _ref2[n];
          p.needsRefresh();
        }
      }
      return true;
    };

    return InventoryPanel;

  })();

  window.JobStage = (function(_super) {
    __extends(JobStage, _super);

    function JobStage() {
      var me;
      me = this;
      this.jobs = {};
      $('.ready').show();
      $('.ready').tap(function() {
        return me.ready.call(me);
      });
      $('.jobstage-interface').show();
      $('.jobstage-interface .box').each(function() {
        var jobcode;
        jobcode = $(this).attr('data-job-type');
        return me.jobs[jobcode] = new JobView($(this));
      });
      $('.jobstage-interface .box').fitText(1, {
        maxFontSize: '40px'
      });
      true;
    }

    JobStage.prototype.ready = function() {
      if (this.getSelectedJob()) {
        $('.ready').addClass('active');
        return pycon.transaction('ready');
      }
    };

    JobStage.prototype.getSelectedJob = function() {
      var job, name, _ref2;
      _ref2 = this.jobs;
      for (name in _ref2) {
        job = _ref2[name];
        if (job.selected) {
          return job;
        }
      }
      return false;
    };

    JobStage.prototype.end = function() {
      var job, name, _i, _len, _ref2;
      $('.jobstage-interface').hide();
      $('.ready').hide().unbind().removeClass('active');
      _ref2 = this.jobs;
      for (job = _i = 0, _len = _ref2.length; _i < _len; job = ++_i) {
        name = _ref2[job];
        j.end.call(j);
      }
      return $('.ready').hide().unbind();
    };

    JobStage.prototype.update_job_selections = function(data) {
      var job, players, _ref2, _results;
      _ref2 = data.job_selections;
      _results = [];
      for (job in _ref2) {
        players = _ref2[job];
        console.log('==> ', job, ' with players ', players);
        this.jobs[job].number_players = players.length;
        _results.push(this.jobs[job].needsRefresh.call(this.jobs[job]));
      }
      return _results;
    };

    return JobStage;

  })(Stage);

  window.JobView = (function() {
    function JobView(dom_object) {
      var me;
      this.dom_object = dom_object;
      me = this;
      this.job = window.jobs[this.dom_object.attr('data-job-type')];
      this.job_code = this.dom_object.attr('data-job-type');
      this.dom_object.css('background-color', this.job.color);
      this.selected = false;
      this.number_players = 0;
      this.dom_object.tap(function() {
        return me.tap.call(me);
      });
      this.needsRefresh();
    }

    JobView.prototype.select = function() {
      var job, q, _ref2;
      _ref2 = window.stage.jobs;
      for (q in _ref2) {
        job = _ref2[q];
        job.unselect.call(job);
      }
      this.selected = true;
      pycon.transaction('job_selected', {
        job: this.job_code
      });
      return this.needsRefresh();
    };

    JobView.prototype.unselect = function() {
      this.selected = false;
      return this.needsRefresh();
    };

    JobView.prototype.tap = function() {
      if (this.selected) {

      } else {
        return this.select();
      }
    };

    JobView.prototype.needsRefresh = function() {
      var player_string;
      this.dom_object.html('');
      this.dom_object.append($("<h3>" + this.job.title + "</h3>"));
      player_string = Array(this.number_players + 1).join("&#9679;");
      this.dom_object.append($("<p>" + player_string + "</p>"));
      if (!this.selected) {
        return this.dom_object.css('opacity', '0.5');
      } else {
        return this.dom_object.css('opacity', '1');
      }
    };

    JobView.prototype.end = function() {
      return this.dom_object.unbind();
    };

    return JobView;

  })();

  window.config = $.ajax({
    type: "GET",
    url: "/configuration.json",
    async: false
  }).responseText;

  try {
    window.config = JSON.parse(window.config);
  } catch (_error) {
    error = _error;
    throw "Configuration loaded from 'configuration.json' is invalid.";
  }

  if ((typeof TEST !== "undefined" && TEST !== null) && TEST === true) {
    $(function() {
      var t;
      console.log("Initializing testing mode.");
      t = new TestSuite();
      return t.run();
    });
  } else {
    $(function() {
      window.socket = new WebSocket("ws://" + location.host + "/json");
      window.jevent('SocketOpened', function() {});
      console.log('The socket was opened.');
      socket.onopen = function() {
        console.log("Socket connection opened successfully.");
        window.pycon = new PyAPI(window.socket);
        return window.go();
      };
      return socket.onclose = function() {
        console.log("Socket connection was closed, unexpectedly.");
        return window.message.display("Oh No!", "I don't know why, but the socket was closed (!)");
      };
    });
  }

  window.go = function() {
    pycon.register_for_event('update_game_info', function(data) {
      console.log('Player count changed: ', data);
      return $('.playercount').html(data.player_count);
    });
    pycon.register_for_event('stage_begin', function(data, responder) {
      if (typeof stage !== "undefined" && stage !== null) {
        window.stage.end();
      }
      if (data.stage_type === 'Job') {
        window.stage = new JobStage();
      } else if (data.stage_type === 'Day') {
        window.stage = new DayStage();
      } else if (data.stage_type === 'Production') {
        window.stage = new ProductionStage();
      } else if (data.stage_type === 'Notification') {
        window.stage = new NotificationStage();
      } else if (data.stage_type === 'Trading') {
        window.stage = new TradingStage();
      } else {
        throw "Illegal stage sent: " + data.stageType;
      }
      return responder.respond();
    });
    pycon.register_for_event('update_player_info', function(data) {
      var amount, name, _ref2;
      _ref2 = data.inventory;
      for (name in _ref2) {
        amount = _ref2[name];
        if (window.stage instanceof TradingStage) {
          player.products[name].amount = amount - window.stage.products[name].for_trade;
        } else {
          player.products[name].amount = amount;
        }
      }
      if (data.condition != null) {
        if (data.condition.health != null) {
          player.setHealth(data.condition.health);
        }
        if (data.condition.antihunger != null) {
          player.setFood(data.condition.antihunger);
        }
      }
      stage.update();
      window.inventorypanel.needsRefresh();
      return window.updateInterface();
    });
    pycon.register_for_event('DisplayMessage', function(data) {
      if (data.clickable == null) {
        data.clickable = true;
      }
      return message.display.call(message, data.title, data.text, data.clickable);
    });
    pycon.register_for_event('InventoryCountRequested', function(data) {
      return pycon.transaction({
        action: data.callback,
        data: player.getInventoryCount.call(player)
      });
    });
    pycon.register_for_event('update_job_selections', function(data) {
      if (stage.update_job_selections != null) {
        return stage.update_job_selections.call(stage, data);
      }
    });
    pycon.register_for_event('display_event', function(data, responder) {
      window.message.display(data.title, data.text);
      return window.message.onclose = (function(_this) {
        return function() {
          return responder.respond({
            response_chosen_id: data.responses[0].id
          });
        };
      })(this);
    });
    pycon.register_for_event('echo', function(data, responder) {
      return responder.respond(data);
    });
    pycon.register_for_event('GivePoints', function(data) {
      return player.givePoints(data.amount);
    });
    pycon.register_for_event('TimerBegin', function(data) {
      console.log('Event handled: ', stage);
      return stage.timer_begin.call(stage, data.duration);
    });
    pycon.register_for_event('RequestProductionReport', function(data) {
      if (stage.report_production != null) {
        return stage.report_production();
      }
    });
    updateStatusBar();
    return window.inventorypanel = new InventoryPanel();
  };

  window.Message = (function() {
    function Message() {
      this.dom_selector = '.message';
      this.timeout = 5;
      this.onclose = (function(_this) {
        return function() {
          return true;
        };
      })(this);
    }

    Message.prototype.display = function(title, text, clickable, duration) {
      var me;
      if (clickable == null) {
        clickable = true;
      }
      if (duration == null) {
        duration = null;
      }
      me = this;
      $('.overlay').show();
      if (text == null) {
        text = '';
      }
      if (title == null) {
        title = '';
      }
      $(this.dom_selector).children('.title').html(title);
      $(this.dom_selector).children('.text').html(text);
      $(this.dom_selector).show();
      if (clickable) {
        $(this.dom_selector).tap(function() {
          return me.hide.call(me);
        });
      }
      if (duration != null) {
        return setTimeout(function() {
          return window.message.hide.call(message);
        }, duration * 1000);
      }
    };

    Message.prototype.hide = function() {
      this.onclose();
      $(this.dom_selector).unbind();
      $(this.dom_selector).hide();
      return $('.overlay').hide();
    };

    return Message;

  })();

  window.message = new Message();

  window.Player = (function() {
    function Player() {
      var p, _i, _len, _ref2;
      this.products = [];
      this.health = 100;
      this.food = 100;
      this.productionfacilities = [];
      _ref2 = ['bandage', 'food', 'bullet', 'log'];
      for (_i = 0, _len = _ref2.length; _i < _len; _i++) {
        p = _ref2[_i];
        this.products[p] = new Product(p);
      }
      this.products['bandage'].color = '#DD514C';
      this.products['food'].color = '#5EB95E';
      this.products['bullet'].color = '#777';
      this.products['log'].color = '#5E2605';
      true;
    }

    Player.prototype.getInventoryCount = function() {
      var inventory, name, p, _ref2;
      inventory = {};
      _ref2 = this.products;
      for (name in _ref2) {
        p = _ref2[name];
        inventory[name] = p.amount;
      }
      return inventory;
    };

    Player.prototype.update = function() {
      this.setHealth(this.health);
      return this.setFood(this.food);
    };

    Player.prototype.setHealth = function(amount) {
      var health_points, health_string;
      if (amount < 100) {
        this.health = amount;
      } else {
        this.health = 100;
      }
      health_points = Math.ceil(this.health / 34.0);
      health_string = Array(health_points + 1).join("&#9829;") + Array(4 - health_points).join("&#9825;");
      return $('.statusbar .health').html(health_string);
    };

    Player.prototype.setFood = function(amount) {
      var food_points, food_string;
      if (amount < 100) {
        this.food = amount;
      } else {
        this.food = 100;
      }
      food_points = Math.ceil(this.food / 33.0);
      food_string = Array(food_points + 1).join("<span class='food'>&nbsp;&nbsp;&nbsp;</span>") + Array(3 - food_points + 1).join("<span class='anti food'>&nbsp;&nbsp;&nbsp;</span>");
      return $('.statusbar .hunger').html(food_string);
    };

    return Player;

  })();

  window.Product = (function() {
    function Product(name) {
      this.name = name;
      this.amount = 0;
      this.color = "green";
      true;
    }

    Product.prototype.activate = function() {
      return pycon.transaction('item_activated', {
        item_name: this.name
      });
    };

    Product.prototype.needsRefresh = function() {
      if (this.amount > 0) {
        return $(".inventory .inventorycount[data-production-type='" + this.name + "']").show().children('span.count').html(this.amount);
      } else {
        return $(".inventory .inventorycount[data-production-type='" + this.name + "']").hide();
      }
    };

    return Product;

  })();

  window.Job = (function() {
    function Job(title, color) {
      this.title = title;
      this.color = color;
      true;
    }

    return Job;

  })();

  window.jobs = {};

  jobs['hospital'] = new Job('Hospital', '#DD514C');

  jobs['production'] = new Job('Production', '#FAD232');

  jobs['farm'] = new Job('Farm', '#5EB95E');

  jobs['watchtower'] = new Job('Watchtower', '#777');

  window.player = new Player();

  window.TestSuite = (function() {
    function TestSuite() {
      var _this = this;
      this.dom_element = $('.test-output');
      this.passed = 0;
      this.test_count = Object.keys(tests).length;
      window.onerror = function() {
        return _this.fail();
      };
      this.failed = false;
    }

    TestSuite.prototype.run = function() {
      console.log("Starting TestSuite...");
      this.passed = 0;
      this.test_keys = Object.keys(tests);
      return this._run_next_test();
    };

    TestSuite.prototype._run_next_test = function() {
      var err, name, test;
      name = this.test_keys.shift();
      if (name == null) {
        console.log("All tests passed.");
        this.dom_element.after("<h1>All tests passed.</h1>");
        this.dom_element.css('color', 'green');
        return;
      }
      test = window.tests[name];
      console.log("Running test '" + name + "'...");
      try {
        if (!test(new TestDelegate(this))) {
          throw "test '" + name + "' returned invalid value";
        }
      } catch (_error) {
        err = _error;
        this.failed = true;
        console.warn("Test '" + name + "' failed with error '" + err + "'");
        throw "Test suite ended due to failed test.";
      }
    };

    TestSuite.prototype.pass = function() {
      this.passed++;
      this.report_state();
      return this._run_next_test();
    };

    TestSuite.prototype.fail = function() {
      this.report_state();
      return this.dom_element.after("<h1 style='color:red'>Test failed</h1>");
    };

    TestSuite.prototype.report_state = function() {
      return this.dom_element.html("" + this.passed + " / " + this.test_count + " tests passed.");
    };

    return TestSuite;

  })();

  window.TestDelegate = (function() {
    function TestDelegate(parent) {
      this.parent = parent;
      true;
    }

    TestDelegate.prototype.pass = function() {
      this.parent.pass();
      return true;
    };

    TestDelegate.prototype.fail = function() {
      this.parent.fail();
      return false;
    };

    return TestDelegate;

  })();

  window.assert = function(statement, error) {
    if (!statement) {
      throw error;
    } else {
      return true;
    }
  };

  window.tests = {
    'Connect to the host': function(t) {
      window.socket = new WebSocket("ws://" + location.host + "/json");
      socket.onopen = function() {
        socket.close();
        return t.pass();
      };
      return true;
    },
    'Start socket, and observe stage_begin': function(t) {
      window.socket = new WebSocket("ws://" + location.host + "/json");
      socket.onopen = function() {
        window.pycon = new PyAPI(window.socket);
        pycon.register_for_event('stage_begin', function(data, responder) {
          responder.respond();
          return setTimeout(function() {
            return t.pass();
          }, 250);
        });
        return window.go();
      };
      return true;
    },
    'Test: update_player_info': function(t) {
      var m;
      m = {
        method: 'update_player_info',
        args: {
          inventory: {
            bandage: Math.round(Math.random() * 100),
            food: Math.round(Math.random() * 100),
            bullet: Math.round(Math.random() * 100),
            log: Math.round(Math.random() * 100)
          },
          condition: {
            health: Math.round(Math.random() * 100),
            antihunger: Math.round(Math.random() * 100)
          }
        }
      };
      pycon.onmessage({
        data: JSON.stringify(m)
      });
      assert(player.products.bandage.amount === m.args.inventory.bandage, "Failed inventory update");
      assert(player.products.food.amount === m.args.inventory.food, "Failed inventory update");
      assert(player.products.bullet.amount === m.args.inventory.bullet, "Failed inventory update");
      assert(player.products.log.amount === m.args.inventory.log, "Failed inventory update");
      assert(player.health === m.args.condition.health, "Failed condition:health update");
      assert(player.food === m.args.condition.antihunger, "Failed condition:antihunger update");
      return t.pass();
    }
  };

  window.TradingStage = (function(_super) {
    __extends(TradingStage, _super);

    function TradingStage() {
      var me,
        _this = this;
      console.log("testing testing");
      me = this;
      this.type = 'TradingStage';
      this.timers = [];
      $('.tradingstage-interface').show();
      player.update();
      $('.health').show();
      $('.hunger').show();
      this.products = {};
      $('.tradingstage-interface .trading span.tradecount').each(function() {
        var type;
        type = $(this).attr('data-production-type');
        $(this).children('.block').css('background-color', player.products[type].color);
        me.products[type] = new TradingProduct($(this), player.products[type]);
        me.products[type].product.needsRefresh();
        me.refreshTradingPlatform();
        return window.inventorypanel.needsRefresh();
      });
      setTimeout(function() {
        var p, _i, _len, _ref2;
        _ref2 = _this.products;
        for (_i = 0, _len = _ref2.length; _i < _len; _i++) {
          p = _ref2[_i];
          p.product.needsRefresh();
        }
        window.inventorypanel.needsRefresh();
        return _this.refreshTradingPlatform();
      }, 300);
      $('.inventory').sortable({
        helper: function(e, ui) {
          var type;
          type = ui.attr('data-production-type');
          if (me.products[type].product.amount <= 0) {
            return $('<div></div>');
          } else {
            return $("<div class='square placeholder'></div>").css('background-color', player.products[ui.attr('data-production-type')].color);
          }
        },
        start: function(e, ui) {
          return ui.item.show();
        },
        change: function() {
          return $(this).sortable("refreshPositions");
        },
        placeholder: 'test',
        stop: function(e, ui) {
          var item, offset;
          offset = ui.originalPosition.top - ui.position.top;
          item = me.products[ui.item.attr('data-production-type')];
          if (offset > 50) {
            item.trade.call(item);
          }
          return $(this).sortable('cancel');
        }
      });
      $('.tradingstage-interface .trading span.tradecount').each(function() {
        var color, type;
        $(this).html("<span class='block'>&#9632;</span> x <span class='count'>0</span>");
        type = $(this).attr('data-production-type');
        color = player.products[type].color;
        $(this).children('.block').css('color', color);
        return $(this).hide();
      });
      $('.inventory span.inventorycount').each(function() {
        var color, type;
        $(this).html("<span class='block'>&#9632;</span> x <span class='count'>0</span>");
        type = $(this).attr('data-production-type');
        color = player.products[type].color;
        $(this).children('.block').css('color', color);
        return $(this).hide();
      });
      $('.trading').on("taphold", function() {
        return _this.clearTrades();
      });
      $('.countdown').show();
      TradingStage.__super__.constructor.apply(this, arguments);
    }

    TradingStage.prototype.end = function() {
      var interval, _i, _len, _ref2;
      $('.countdown').hide();
      $('.ready').hide().unbind().removeClass('active');
      $('.tradingstage-interface').hide();
      $('.trading').unbind();
      $('.health').hide();
      $('.hunger').hide();
      $('.tradingstage-interface .inventory').sortable('destroy');
      if ($('.placeholder').length > 0) {
        $('.placeholder').remove();
      }
      this.clearTrades();
      _ref2 = this.timers;
      for (_i = 0, _len = _ref2.length; _i < _len; _i++) {
        interval = _ref2[_i];
        clearInterval(interval);
      }
      return TradingStage.__super__.end.apply(this, arguments);
    };

    TradingStage.prototype.bump = function() {
      var items, name, p, _ref2,
        _this = this;
      items = {};
      _ref2 = this.products;
      for (name in _ref2) {
        p = _ref2[name];
        if (p.for_trade > 0) {
          items[name] = p.for_trade;
        }
      }
      return pycon.transaction('trade_proposed', {
        items: items
      }, function(r) {
        var amount, _ref3, _ref4;
        _ref3 = _this.products;
        for (name in _ref3) {
          p = _ref3[name];
          p.for_trade = 0;
        }
        _ref4 = r.items;
        for (name in _ref4) {
          amount = _ref4[name];
          _this.products[name].for_trade = amount;
        }
        window.inventorypanel.needsRefresh();
        return _this.refreshTradingPlatform();
      });
    };

    TradingStage.prototype.clearTrades = function() {
      var name, p, _ref2;
      _ref2 = this.products;
      for (name in _ref2) {
        p = _ref2[name];
        if (p.for_trade > 0) {
          p.product.amount += p.for_trade;
          p.for_trade = 0;
          p.needsRefresh.call(p);
        }
      }
      this.refreshTradingPlatform();
      return window.inventorypanel.needsRefresh();
    };

    TradingStage.prototype.trade_complete = function(data) {
      var amount, card, name, p, _i, _len, _ref2, _ref3, _ref4;
      _ref2 = this.products;
      for (name in _ref2) {
        p = _ref2[name];
        p.for_trade = 0;
      }
      _ref3 = player.cards;
      for (_i = 0, _len = _ref3.length; _i < _len; _i++) {
        card = _ref3[_i];
        card.on_trade_end.call(card, data.items);
      }
      _ref4 = data.items;
      for (name in _ref4) {
        amount = _ref4[name];
        if (this.products[name] != null) {
          this.products[name].for_trade = amount;
          this.products[name].needsRefresh.call(this.products[name]);
        }
      }
      return this.refreshTradingPlatform();
    };

    TradingStage.prototype.price_updated = function() {
      var name, p, _ref2, _results;
      _ref2 = this.products;
      _results = [];
      for (name in _ref2) {
        p = _ref2[name];
        _results.push(p.needsRefresh.call(p));
      }
      return _results;
    };

    TradingStage.prototype.products_updated = function() {
      return this.price_updated();
    };

    TradingStage.prototype.update = function() {
      this.price_updated();
      this.refreshTradingPlatform();
      return window.inventorypanel.needsRefresh();
    };

    TradingStage.prototype.refreshTradingPlatform = function() {
      var name, p, _ref2, _results;
      _ref2 = this.products;
      _results = [];
      for (name in _ref2) {
        p = _ref2[name];
        if (p.for_trade > 0) {
          _results.push($(".tradingstage-interface .tradecount[data-production-type='" + name + "']").show().children('.count').html(p.for_trade));
        } else {
          _results.push($(".tradingstage-interface .tradecount[data-production-type='" + name + "']").hide());
        }
      }
      return _results;
    };

    TradingStage.prototype.yield_production = function() {
      var card, facility, name, p, _i, _len, _ref2, _ref3, _results;
      _ref2 = this.products;
      for (name in _ref2) {
        p = _ref2[name];
        facility = player.productionfacilities[name];
        facility.run_factory.call(facility);
        p.needsRefresh.call(p);
      }
      _ref3 = player.cards;
      _results = [];
      for (_i = 0, _len = _ref3.length; _i < _len; _i++) {
        card = _ref3[_i];
        _results.push(card.on_production.call(card));
      }
      return _results;
    };

    TradingStage.prototype.refreshCards = function() {
      var card, deck, element, index, _i, _len, _ref2;
      deck = $('.powerups .deck');
      deck.html("");
      index = 0;
      _ref2 = player.cards;
      for (_i = 0, _len = _ref2.length; _i < _len; _i++) {
        card = _ref2[_i];
        console.log('Adding card: ', card);
        element = $("<div class='card' data-card-index='" + index + "'>" + (card.render.call(card)) + "</div>").tap(function() {
          card = player.cards[$(this).attr('data-card-index')];
          return card.activate.call(card);
        });
        element.appendTo(deck);
        index += 1;
      }
      return $('.tradingstage-interface .card').fitText(1, {
        minFontSize: '25px'
      });
    };

    TradingStage.prototype.timer_begin = function(countdown) {
      var count_down, me;
      me = this;
      this.time = countdown;
      count_down = function() {
        if (stage.time > 0) {
          stage.time -= 1;
        }
        return updateCountdown();
      };
      this.timers.push(setInterval(count_down, 1000));
      return updateCountdown();
    };

    return TradingStage;

  })(Stage);

  window.TradingProduct = (function() {
    function TradingProduct(dom_element, product) {
      this.dom_element = dom_element;
      this.product = product;
      this.needsRefresh();
      this.for_trade = 0;
      true;
    }

    TradingProduct.prototype.trade = function() {
      if (this.product.amount > 0) {
        this.for_trade += 1;
        this.product.amount -= 1;
        this.needsRefresh();
        window.inventorypanel.needsRefresh();
        stage.refreshTradingPlatform.call(stage);
        return true;
      } else {
        return false;
      }
    };

    TradingProduct.prototype.sell = function() {
      return true;
    };

    TradingProduct.prototype.needsRefresh = function() {
      return true;
    };

    return TradingProduct;

  })();

}).call(this);
