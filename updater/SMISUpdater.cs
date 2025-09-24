using System;
using System.Diagnostics;
using System.IO;
using System.Net.Http;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace SMISUpdater
{
    public partial class UpdateChecker : Form
    {
        private const string GITHUB_API_URL = "https://api.github.com/repos/ZubairHussainK/smis/releases/latest";
        private const string CURRENT_VERSION = "2.0.0"; // This should match your version.py
        private const string ENCRYPT_KEY = "YOUR_ENCRYPT_KEY_HERE"; // Same as GitHub Actions secret
        
        private static readonly HttpClient httpClient = new HttpClient();
        
        public UpdateChecker()
        {
            InitializeComponent();
            this.Load += UpdateChecker_Load;
        }
        
        private async void UpdateChecker_Load(object sender, EventArgs e)
        {
            await CheckForUpdates();
        }
        
        private async Task CheckForUpdates()
        {
            try
            {
                // Check internet connection
                if (!await IsInternetAvailable())
                {
                    Console.WriteLine("No internet connection. Skipping update check.");
                    LaunchMainApplication();
                    return;
                }
                
                Console.WriteLine("Checking for updates...");
                
                // Get latest release info
                var releaseInfo = await GetLatestReleaseInfo();
                if (releaseInfo == null)
                {
                    Console.WriteLine("Could not fetch release information.");
                    LaunchMainApplication();
                    return;
                }
                
                // Compare versions
                if (IsNewerVersion(releaseInfo.TagName, CURRENT_VERSION))
                {
                    ShowUpdateDialog(releaseInfo);
                }
                else
                {
                    Console.WriteLine("Application is up to date.");
                    LaunchMainApplication();
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error checking for updates: {ex.Message}");
                LaunchMainApplication();
            }
        }
        
        private async Task<bool> IsInternetAvailable()
        {
            try
            {
                using (var response = await httpClient.GetAsync("https://www.google.com", 
                    HttpCompletionOption.ResponseHeadersRead))
                {
                    return response.IsSuccessStatusCode;
                }
            }
            catch
            {
                return false;
            }
        }
        
        private async Task<GitHubRelease> GetLatestReleaseInfo()
        {
            try
            {
                httpClient.DefaultRequestHeaders.Clear();
                httpClient.DefaultRequestHeaders.Add("User-Agent", "SMIS-Updater");
                
                var response = await httpClient.GetStringAsync(GITHUB_API_URL);
                var options = new JsonSerializerOptions
                {
                    PropertyNamingPolicy = JsonNamingPolicy.CamelCase
                };
                
                return JsonSerializer.Deserialize<GitHubRelease>(response, options);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error fetching release info: {ex.Message}");
                return null;
            }
        }
        
        private bool IsNewerVersion(string latestVersion, string currentVersion)
        {
            // Remove 'v' prefix if present
            latestVersion = latestVersion.TrimStart('v');
            currentVersion = currentVersion.TrimStart('v');
            
            try
            {
                var latest = new Version(latestVersion);
                var current = new Version(currentVersion);
                return latest > current;
            }
            catch
            {
                return false;
            }
        }
        
        private void ShowUpdateDialog(GitHubRelease release)
        {
            var result = MessageBox.Show(
                $"A new update is available!\n\n" +
                $"Current Version: v{CURRENT_VERSION}\n" +
                $"Latest Version: {release.TagName}\n\n" +
                $"Do you want to download and install it?",
                "Update Available",
                MessageBoxButtons.YesNo,
                MessageBoxIcon.Information
            );
            
            if (result == DialogResult.Yes)
            {
                _ = DownloadAndInstallUpdate(release);
            }
            else
            {
                LaunchMainApplication();
            }
        }
        
        private async Task DownloadAndInstallUpdate(GitHubRelease release)
        {
            try
            {
                // Find the encrypted installer asset
                var asset = FindInstallerAsset(release);
                if (asset == null)
                {
                    MessageBox.Show("Could not find installer in release assets.", "Update Error", 
                        MessageBoxButtons.OK, MessageBoxIcon.Error);
                    LaunchMainApplication();
                    return;
                }
                
                // Show progress dialog
                using (var progressForm = new ProgressForm())
                {
                    progressForm.Show();
                    progressForm.UpdateStatus("Downloading update...");
                    
                    // Download encrypted file
                    var tempDir = Path.GetTempPath();
                    var encryptedPath = Path.Combine(tempDir, asset.Name);
                    var decryptedPath = Path.Combine(tempDir, asset.Name.Replace("-encrypted", ""));
                    
                    await DownloadFile(asset.BrowserDownloadUrl, encryptedPath, progressForm);
                    
                    progressForm.UpdateStatus("Decrypting installer...");
                    
                    // Decrypt the installer
                    if (DecryptFile(encryptedPath, decryptedPath))
                    {
                        progressForm.UpdateStatus("Starting installation...");
                        
                        // Run the installer
                        var process = Process.Start(new ProcessStartInfo
                        {
                            FileName = decryptedPath,
                            Arguments = "/S", // Silent install (adjust based on your installer)
                            UseShellExecute = true,
                            Verb = "runas" // Run as administrator
                        });
                        
                        // Exit current application to allow installation
                        Environment.Exit(0);
                    }
                    else
                    {
                        MessageBox.Show("Failed to decrypt installer.", "Update Error", 
                            MessageBoxButtons.OK, MessageBoxIcon.Error);
                        LaunchMainApplication();
                    }
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error during update: {ex.Message}", "Update Error", 
                    MessageBoxButtons.OK, MessageBoxIcon.Error);
                LaunchMainApplication();
            }
        }
        
        private GitHubAsset FindInstallerAsset(GitHubRelease release)
        {
            foreach (var asset in release.Assets)
            {
                if (asset.Name.EndsWith("-encrypted.exe", StringComparison.OrdinalIgnoreCase))
                {
                    return asset;
                }
            }
            return null;
        }
        
        private async Task DownloadFile(string url, string filePath, ProgressForm progressForm)
        {
            using (var response = await httpClient.GetAsync(url, HttpCompletionOption.ResponseHeadersRead))
            {
                response.EnsureSuccessStatusCode();
                
                var totalBytes = response.Content.Headers.ContentLength ?? 0;
                using (var contentStream = await response.Content.ReadAsStreamAsync())
                using (var fileStream = new FileStream(filePath, FileMode.Create, FileAccess.Write))
                {
                    var buffer = new byte[8192];
                    long downloadedBytes = 0;
                    int bytesRead;
                    
                    while ((bytesRead = await contentStream.ReadAsync(buffer, 0, buffer.Length)) > 0)
                    {
                        await fileStream.WriteAsync(buffer, 0, bytesRead);
                        downloadedBytes += bytesRead;
                        
                        if (totalBytes > 0)
                        {
                            var percentage = (int)((downloadedBytes * 100) / totalBytes);
                            progressForm.UpdateProgress(percentage);
                        }
                    }
                }
            }
        }
        
        private bool DecryptFile(string encryptedPath, string decryptedPath)
        {
            try
            {
                // Convert the key using the same method as the Python encryption
                byte[] keyBytes = DeriveKey(ENCRYPT_KEY);
                string base64Key = Convert.ToBase64String(keyBytes).Replace('+', '-').Replace('/', '_');
                
                using (var aes = Aes.Create())
                {
                    // Read encrypted data
                    var encryptedData = File.ReadAllBytes(encryptedPath);
                    
                    // For Fernet-style decryption (Python cryptography library compatible)
                    var decryptedData = FernetDecrypt(encryptedData, base64Key);
                    
                    File.WriteAllBytes(decryptedPath, decryptedData);
                    
                    // Clean up encrypted file
                    File.Delete(encryptedPath);
                    
                    return true;
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Decryption error: {ex.Message}");
                return false;
            }
        }
        
        private byte[] DeriveKey(string password)
        {
            // Use the same key derivation as in the Python script
            using (var pbkdf2 = new Rfc2898DeriveBytes(
                Encoding.UTF8.GetBytes(password), 
                Encoding.UTF8.GetBytes("smis_salt_2024"), 
                100000, 
                HashAlgorithmName.SHA256))
            {
                return pbkdf2.GetBytes(32); // 256 bits
            }
        }
        
        private byte[] FernetDecrypt(byte[] encryptedData, string base64Key)
        {
            // This is a simplified Fernet-compatible decryption
            // For production, consider using a proper Fernet library for .NET
            // or implement the full Fernet specification
            
            using (var aes = Aes.Create())
            {
                var key = Convert.FromBase64String(base64Key.Replace('-', '+').Replace('_', '/'));
                
                // Extract IV from the beginning of the encrypted data (Fernet format)
                var iv = new byte[16];
                var ciphertext = new byte[encryptedData.Length - 16];
                
                Array.Copy(encryptedData, 0, iv, 0, 16);
                Array.Copy(encryptedData, 16, ciphertext, 0, ciphertext.Length);
                
                aes.Key = key;
                aes.IV = iv;
                aes.Mode = CipherMode.CBC;
                aes.Padding = PaddingMode.PKCS7;
                
                using (var decryptor = aes.CreateDecryptor())
                {
                    return decryptor.TransformFinalBlock(ciphertext, 0, ciphertext.Length);
                }
            }
        }
        
        private void LaunchMainApplication()
        {
            try
            {
                // Launch your main Python application
                Process.Start(new ProcessStartInfo
                {
                    FileName = "python",
                    Arguments = "main.py",
                    UseShellExecute = true,
                    WorkingDirectory = Application.StartupPath
                });
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error launching main application: {ex.Message}");
                MessageBox.Show("Error launching SMIS application.", "Launch Error", 
                    MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
            finally
            {
                Application.Exit();
            }
        }
        
        private void InitializeComponent()
        {
            this.SuspendLayout();
            // 
            // UpdateChecker
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(0, 0);
            this.FormBorderStyle = FormBorderStyle.None;
            this.Name = "UpdateChecker";
            this.Text = "SMIS Update Checker";
            this.WindowState = FormWindowState.Minimized;
            this.ShowInTaskbar = false;
            this.ResumeLayout(false);
        }
    }
    
    // Data models for GitHub API
    public class GitHubRelease
    {
        public string TagName { get; set; }
        public string Name { get; set; }
        public string Body { get; set; }
        public GitHubAsset[] Assets { get; set; }
    }
    
    public class GitHubAsset
    {
        public string Name { get; set; }
        public string BrowserDownloadUrl { get; set; }
        public long Size { get; set; }
    }
    
    // Progress dialog
    public partial class ProgressForm : Form
    {
        private Label statusLabel;
        private ProgressBar progressBar;
        
        public ProgressForm()
        {
            InitializeComponent();
        }
        
        public void UpdateStatus(string status)
        {
            if (InvokeRequired)
            {
                Invoke(new Action<string>(UpdateStatus), status);
                return;
            }
            statusLabel.Text = status;
        }
        
        public void UpdateProgress(int percentage)
        {
            if (InvokeRequired)
            {
                Invoke(new Action<int>(UpdateProgress), percentage);
                return;
            }
            progressBar.Value = Math.Min(100, Math.Max(0, percentage));
        }
        
        private void InitializeComponent()
        {
            this.statusLabel = new Label();
            this.progressBar = new ProgressBar();
            this.SuspendLayout();
            
            // statusLabel
            this.statusLabel.AutoSize = true;
            this.statusLabel.Location = new System.Drawing.Point(12, 15);
            this.statusLabel.Size = new System.Drawing.Size(200, 13);
            this.statusLabel.Text = "Initializing...";
            
            // progressBar
            this.progressBar.Location = new System.Drawing.Point(12, 40);
            this.progressBar.Size = new System.Drawing.Size(360, 23);
            this.progressBar.Style = ProgressBarStyle.Continuous;
            
            // ProgressForm
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(384, 80);
            this.Controls.Add(this.statusLabel);
            this.Controls.Add(this.progressBar);
            this.FormBorderStyle = FormBorderStyle.FixedDialog;
            this.MaximizeBox = false;
            this.MinimizeBox = false;
            this.Name = "ProgressForm";
            this.StartPosition = FormStartPosition.CenterScreen;
            this.Text = "SMIS Update";
            this.ResumeLayout(false);
            this.PerformLayout();
        }
    }
    
    // Main Program
    public static class Program
    {
        [STAThread]
        public static void Main()
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            Application.Run(new UpdateChecker());
        }
    }
}