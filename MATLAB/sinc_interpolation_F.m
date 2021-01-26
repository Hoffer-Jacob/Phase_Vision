function interpolated = sinc_interpolation_F(sampled,t,ts)
% sinc_interpolation_F ruturs interpolated values the sampled waeform
%   sampled: sampled waveform
%   ts: the time

[Ts,T] = ndgrid(ts,t);
interpolated = sinc(Ts - T) * sampled;
end

