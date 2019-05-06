from simple_pid import PID

from data_science.tools.threading_utilities import StoppableThread


class PIDController():
    """Implements a PID controller in a stoppable thread."""

    def __init__(self, kp, ki, kd, bottom_output_limit=0, upper_output_limit=1,
                 sample_time=0.1):
        self.pid = PID(Kp=kp, Ki=ki, Kd=kd, sample_time=sample_time)
        self.pid.output_limits = (bottom_output_limit, upper_output_limit)
        self.output = 0
        self.input = 0
        self.in_parameter = None
        self.out_parameter = None

    def setpoint(self, setpoint):
        """
        Define a setpoint.
            :param self: self
            :param setpoint: setpoint for the PID
        """
        self.pid.setpoint = setpoint

    def output_limits(self, bottom, upper):
        """
        Define the output limits.
            :param self: self
            :param bottom: bottom limit
            :param upper: upper limit
        """
        self.pid.output_limits = (bottom, upper)

    def input_parameter(self, parameter):
        """
        Provide a parameter to read the input.
            :param self: self
            :param parameter: a parameter object, with an input channel.
        """
        self.in_parameter = parameter

    def output_parameter(self, parameter):
        """
        Provide a parameter to write the output.
            :param self: self
            :param parameter: a parameter object, with an output channel.
        """
        self.out_parameter = parameter

    def run(self):
        while True:
            # read from channel
            if self.in_parameter is not None:
                self.input = self.in_parameter.read_from_channel()
            # execute the PID controller
            self.output = self.pid(self.input)
            # write to channel
            if self.out_parameter is not None:
                self.out_parameter.write_to_channel(self.output)
            # stop the thread if necessary
            if self.thread.stopped():
                break

    def start(self):
        """
        Start the thread.
            :param self: self
        """
        self.thread = StoppableThread(target=self.run)
        self.thread.start()

    def stop(self):
        """
        Stop the thread.
            :param self: self
        """
        self.thread.stop()
        self.thread.join()
