import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  AppBar, Toolbar, Typography, Box, Drawer, List, ListItemButton,
  ListItemIcon, ListItemText, IconButton, Avatar, Menu, MenuItem,
  Divider, useTheme, Tooltip, useMediaQuery,
} from '@mui/material';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faHome, faPalette, faRightFromBracket, faUser, faBars,
  faWandMagicSparkles, faChevronLeft,
} from '@fortawesome/free-solid-svg-icons';
import { useState } from 'react';
import { useAuthStore } from '../store';

const DRAWER_WIDTH = 260;

export default function Layout() {
  const theme = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuthStore();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [drawerOpen, setDrawerOpen] = useState(true);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const menuItems = [
    { text: 'Dashboard', icon: faHome, path: '/' },
    { text: 'Style Explorer', icon: faPalette, path: '/styles' },
  ];

  const handleLogout = () => {
    setAnchorEl(null);
    logout();
    navigate('/login');
  };

  const drawerContent = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ p: 3, display: 'flex', alignItems: 'center', gap: 1.5 }}>
        <FontAwesomeIcon icon={faWandMagicSparkles} style={{ color: theme.palette.primary.main, fontSize: 24 }} />
        <Typography variant="h6" sx={{ fontFamily: '"Playfair Display", serif', fontWeight: 700 }}>
          DesignAI
        </Typography>
        {!isMobile && (
          <IconButton
            onClick={() => setDrawerOpen(false)}
            size="small"
            sx={{ ml: 'auto' }}
          >
            <FontAwesomeIcon icon={faChevronLeft} style={{ fontSize: 14 }} />
          </IconButton>
        )}
      </Box>
      <Divider />
      <List sx={{ flex: 1, px: 1.5, pt: 2 }}>
        {menuItems.map((item) => (
          <ListItemButton
            key={item.path}
            selected={location.pathname === item.path}
            onClick={() => {
              navigate(item.path);
              setMobileOpen(false);
            }}
            sx={{
              borderRadius: 2,
              mb: 0.5,
              '&.Mui-selected': {
                backgroundColor: `${theme.palette.primary.main}14`,
                color: theme.palette.primary.main,
                '& .MuiListItemIcon-root': { color: theme.palette.primary.main },
              },
            }}
          >
            <ListItemIcon sx={{ minWidth: 40 }}>
              <FontAwesomeIcon icon={item.icon} />
            </ListItemIcon>
            <ListItemText primary={item.text} />
          </ListItemButton>
        ))}
      </List>
    </Box>
  );

  const currentDrawerWidth = drawerOpen ? DRAWER_WIDTH : 0;

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      {/* Desktop Sidebar */}
      {!isMobile && (
        <Drawer
          variant="persistent"
          open={drawerOpen}
          sx={{
            width: currentDrawerWidth,
            flexShrink: 0,
            transition: theme.transitions.create('width', {
              easing: theme.transitions.easing.sharp,
              duration: theme.transitions.duration.enteringScreen,
            }),
            '& .MuiDrawer-paper': {
              width: DRAWER_WIDTH,
              borderRight: '1px solid #e2e8f0',
              boxSizing: 'border-box',
            },
          }}
        >
          {drawerContent}
        </Drawer>
      )}

      {/* Mobile Sidebar */}
      {isMobile && (
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={() => setMobileOpen(false)}
          sx={{
            '& .MuiDrawer-paper': { width: DRAWER_WIDTH },
          }}
        >
          {drawerContent}
        </Drawer>
      )}

      {/* Main Content */}
      <Box
        sx={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          minWidth: 0,
          transition: theme.transitions.create('margin-left', {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.enteringScreen,
          }),
        }}
      >
        <AppBar
          position="sticky"
          color="inherit"
          elevation={0}
          sx={{ borderBottom: '1px solid #e2e8f0', backgroundColor: 'white' }}
        >
          <Toolbar>
            <Tooltip title={drawerOpen ? 'Close sidebar' : 'Open sidebar'}>
              <IconButton
                onClick={() => {
                  if (isMobile) {
                    setMobileOpen(true);
                  } else {
                    setDrawerOpen((prev) => !prev);
                  }
                }}
                sx={{ mr: 2 }}
              >
                <FontAwesomeIcon icon={faBars} />
              </IconButton>
            </Tooltip>
            <Box sx={{ flex: 1 }} />
            <IconButton onClick={(e) => setAnchorEl(e.currentTarget)}>
              <Avatar sx={{ width: 36, height: 36, bgcolor: theme.palette.primary.main, fontSize: 14 }}>
                {user?.name?.charAt(0).toUpperCase()}
              </Avatar>
            </IconButton>
            <Menu
              anchorEl={anchorEl}
              open={Boolean(anchorEl)}
              onClose={() => setAnchorEl(null)}
              transformOrigin={{ vertical: 'top', horizontal: 'right' }}
              anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
            >
              <MenuItem disabled>
                <FontAwesomeIcon icon={faUser} style={{ marginRight: 10 }} />
                {user?.name}
              </MenuItem>
              <Divider />
              <MenuItem onClick={handleLogout}>
                <FontAwesomeIcon icon={faRightFromBracket} style={{ marginRight: 10 }} />
                Logout
              </MenuItem>
            </Menu>
          </Toolbar>
        </AppBar>
        <Box sx={{ flex: 1, p: { xs: 2, md: 3 }, overflow: 'auto' }}>
          <Outlet />
        </Box>
      </Box>
    </Box>
  );
}
