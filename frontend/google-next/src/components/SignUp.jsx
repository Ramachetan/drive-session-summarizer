import * as React from 'react';
import Button from '@mui/material/Button';
import CssBaseline from '@mui/material/CssBaseline';
import TextField from '@mui/material/TextField';
import Link from '@mui/material/Link';
import Paper from '@mui/material/Paper';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import MiracleLogo from '../assets/Miracle Logo.svg';
import rectangle1 from '../assets/Rectangle1.svg';
import rectangle2 from '../assets/Rectangle2.svg';
import text1 from '../assets/Text1.svg';
import text2 from '../assets/Text2.svg';
import gemini from '../assets/gemini.svg';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import axios from 'axios';
import PlayCircleFilledWhiteIcon from '@mui/icons-material/PlayCircleFilledWhite';
import background from '../assets/car.jpg';
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';


const defaultTheme = createTheme();


export default function SignInSide() {

  const navigate = useNavigate();
  useEffect(() => {

    document.body.style.overflow = 'hidden';
    document.getElementById('root').style.height = '100vh';
    document.getElementById('root').style.width = '100vw';
  }, []);

  const handleSubmit = async (event) => {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    const player_id = data.get('name').toString();
    try {
      const response = await axios.post('http://127.0.0.1:8000/generate_summary/', {
        player_id: player_id
      }, {
        headers: {
          'Content-Type': 'application/json'
        }
      });
      console.log(response.data);
      navigate('/response', { state: { apiResponse: response.data.generated_text , player_id: response.data.player_id} });
    } catch (error) {
      console.error('Error generating summary:', error);
    }
  };

  return (
    <ThemeProvider theme={defaultTheme}>
      <header style={{
        background: '#232527',
        height: '80px',
        display: 'flex',
        alignItems: 'center',
        paddingLeft: '10px',
        paddingRight: '10px',
      }}>
        <div className="logo">
          <img src={MiracleLogo} alt="Miracle Logo" style={{ width: '180px', height: '140px', }} />
        </div>
      </header>
      <Grid container component="main" sx={{ height: '100%' }}>
        <CssBaseline />
        <Grid
          item
          xs={false}
          sm={4}
          md={7}
          sx={{
            backgroundImage: `url('${background}')`,
            backgroundPosition: 'center',
            backgroundSize: 'cover',
            backgroundRepeat: 'no-repeat',
            backgroundColor: (t) =>
              t.palette.mode === 'light' ? t.palette.grey[50] : t.palette.grey[900],
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center',
          }}
        >
        {/* Rectangle 1 container */}
        {/* <div style={{ position: 'relative', width: '100%', marginBottom: '10px', transform: 'translateY(-90%)' }}>
          <img src={rectangle1} alt="Rectangle 1" style={{ width: '100%', height: 'auto' }} />
          <img src={text1} alt="Text 1" style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', width: '50%', height: 'auto' }} />
        </div> */}

        {/* Rectangle 2 container */}
        {/* <div style={{ position: 'relative', width: '100%', transform: 'translateY(-70%)' }}>
          <img src={rectangle2} alt="Rectangle 2" style={{ width: '100%', height: 'auto' }} />
          <img src={text2} alt="Text 2" style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', width: '50%', height: 'auto' }} />
        </div> */}

        </Grid>

        <Grid item xs={12} sm={8} md={5} component={Paper} elevation={0} square>
          <Box
            sx={{
              my: 8,
              mx: 4,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
            }}
          >
            <svg style={{ fontSize: '100px' }} width="0" height="0">
              <linearGradient id="gradient-icon" gradientTransform="rotate(90)">
                <stop offset="5%" stopColor="#4A90E7" />
                <stop offset="95%" stopColor="#C6667B" />
              </linearGradient>
            </svg>
            <AutoAwesomeIcon style={{ fill: 'url(#gradient-icon)', fontSize: '100px' }} />
            <h1 style={{ color: '#232527', fontFamily: 'Lato', fontWeight: 'bold' }}>Sign up to continue</h1>

            <Box
              component="form"
              onSubmit={handleSubmit}
              sx={{
                my: 1,
                mx: 4,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                width: '100%',
              }}
            >
              <TextField
                margin="normal"
                required
                fullWidth
                id="name"
                placeholder="Name"
                name="name"
                autoComplete="name"
                autoFocus
                variant='standard'
                sx={{
                  '& .MuiInputBase-input': {
                    height: '70px',
                    fontSize: '2.5rem',
                    fontFamily: 'Lato',
                  },
                  '& .MuiOutlinedInput-root': {
                    borderRadius: '35px',
                  },
                  my: 1,
                }}
              />
              <TextField
                margin="normal"
                required
                fullWidth
                id="email"
                placeholder="Email Address"
                name="email"
                autoComplete="email"
                variant='standard'
                sx={{
                  '& .MuiInputBase-input': {
                    height: '70px',
                    fontSize: '2.5rem',
                    fontFamily: 'Lato',
                  },
                  '& .MuiOutlinedInput-root': {
                    borderRadius: '35px',
                  },
                  my: 1,
                }}
              />
              <TextField
                margin="normal"
                required
                fullWidth
                id="Phone"
                placeholder="Phone Number"
                name="Phone"
                autoComplete="Phone"
                variant='standard'
                sx={{
                  '& .MuiInputBase-input': {
                    height: '70px',
                    fontSize: '2.5rem',
                    fontFamily: 'Lato',
                  },
                  '& .MuiOutlinedInput-root': {
                    borderRadius: '35px',
                  },
                  my: 1,
                }}
              />

              <Button
                type="submit"
                fullWidth
                variant="contained"
                endIcon={<PlayCircleFilledWhiteIcon
                  style={{ fontSize: 35 }}
                />}
                sx={{
                  mt: 4,
                  mb: 2,
                  backgroundColor: '#0D416B',
                  color: '#ffffff',
                  fontWeight: 'bold',
                  fontFamily: 'Lato',
                  padding: '20px',
                  height: '70px',
                  width: '200px',
                  fontSize: '2rem',
                }}
              >
                Start
              </Button>
              {/* Gemini container */}
              <div style={{ position: 'relative', width: '30%', transform: 'translateY(30%)' }}>
                <img src={gemini} alt="Gemini" style={{ width: '100%', height: 'auto' }} />
              </div>
            </Box>
          </Box>
        </Grid>
      </Grid>
    </ThemeProvider>
  );
}
